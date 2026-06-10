# Background Jobs with Solid Queue

Solid Queue is the default Active Job backend in Rails 8. It's database-backed
(no Redis), supports concurrency controls, recurring jobs, and priorities, and
runs either as a standalone supervisor (`bin/jobs`) or inside Puma.

Because it's a plain Active Job adapter, **all job behavior uses the standard
Active Job API** (`queue_as`, `retry_on`, `discard_on`, `perform_later`). There
is no `sidekiq_options`.

## Setup

```bash
bundle add solid_queue
bin/rails solid_queue:install
```

This creates `config/queue.yml`, `config/recurring.yml`, `db/queue_schema.rb`,
and a `bin/jobs` executable, and sets the production adapter.

### Use a separate database (recommended)

```yaml
# config/database.yml
production:
  primary:
    <<: *default
    database: storage/production.sqlite3
  queue:
    <<: *default
    database: storage/production_queue.sqlite3
    migrations_paths: db/queue_migrate
```

```ruby
# config/environments/production.rb
config.active_job.queue_adapter = :solid_queue
config.solid_queue.connects_to = { database: { writing: :queue } }
```

For PostgreSQL/MySQL, point the `queue` entry at a dedicated database instead of
a SQLite file. To use a single database, fold `db/queue_schema.rb` into a normal
migration and drop the `connects_to` line.

Run `bin/rails db:prepare` to create and load all databases.

### Worker & dispatcher configuration

```yaml
# config/queue.yml
production:
  dispatchers:
    - polling_interval: 1
      batch_size: 500
      concurrency_maintenance_interval: 300
  workers:
    - queues: "*"
      threads: 3
      polling_interval: 2
    - queues: [real_time, background]
      threads: 5
      polling_interval: 0.1
      processes: 3
```

- `threads` — thread pool size per worker process (default 3)
- `processes` — worker processes forked (default 1)
- `queues` — exact names, a wildcard (`staging*`), or `"*"` for all. Prefer exact
  names on large apps; broad wildcards hurt polling performance.

## Running Solid Queue

```bash
bin/jobs                    # start the supervisor (workers + dispatcher + scheduler)
bin/jobs --skip-recurring   # skip the recurring scheduler
```

Or run it inside the Puma process (one fewer process to operate):

```ruby
# config/puma.rb
plugin :solid_queue if ENV["SOLID_QUEUE_IN_PUMA"] || Rails.env.development?
```

## Basic Job Design

```ruby
# app/jobs/email_sender_job.rb
class EmailSenderJob < ApplicationJob
  queue_as :default

  def perform(user_id, email_type)
    user = User.find(user_id)
    UserMailer.send(email_type, user).deliver_now
  end
end

# Usage
EmailSenderJob.perform_later(user.id, :welcome)

# Perform at a specific time
EmailSenderJob.set(wait: 1.hour).perform_later(user.id, :reminder)
EmailSenderJob.set(wait_until: Date.tomorrow.noon).perform_later(user.id, :digest)

# Bulk enqueue in a single round-trip (Active Job perform_all_later)
jobs = user_ids.map { |id| EmailSenderJob.new(id, :newsletter) }
ActiveJob.perform_all_later(jobs)
```

> Always pass IDs, not records. Active Job serializes arguments via GlobalID;
> passing an unsaved record raises, and passing a fat object bloats the queue row.

## Queue Priority

Solid Queue picks jobs by queue order and an optional numeric `priority`
(**lower runs first**).

```ruby
class CriticalJob < ApplicationJob
  queue_as :critical
  def perform; end
end

class ReportGenerationJob < ApplicationJob
  queue_as :low
  def perform; end
end

# Per-enqueue priority within a queue
NotifyJob.set(priority: 10).perform_later(user.id)
```

Make the worker honor queue order by listing queues most-important-first:

```yaml
# config/queue.yml
workers:
  - queues: [critical, default, low]
    threads: 5
```

## Retry Strategy

Retries are Active Job's job, executed by Solid Queue. `:polynomially_longer` is
the Rails 8 default backoff (≈ attempt ** 4 + jitter).

```ruby
class ImportJob < ApplicationJob
  # Retry transient failures with growing backoff
  retry_on Net::OpenTimeout, wait: :polynomially_longer, attempts: 5

  # Fixed backoff for a known rate-limited dependency
  retry_on RateLimitError, wait: 1.hour, attempts: 10

  # Don't retry unrecoverable cases — drop the job
  discard_on ActiveJob::DeserializationError

  def perform(data_url)
    # Import logic
  end
end
```

## Error Handling

Report errors centrally and decide retry vs. discard explicitly.

```ruby
# app/jobs/application_job.rb
class ApplicationJob < ActiveJob::Base
  # Send every job exception to the unified Rails error reporter
  rescue_from(Exception) do |exception|
    Rails.error.report(exception)
    raise exception
  end
end

class ProcessPaymentJob < ApplicationJob
  retry_on PaymentError, wait: :polynomially_longer, attempts: 3

  # Runs after retries are exhausted (block receives the job and the error)
  discard_on ActiveJob::DeserializationError

  after_discard do |job, error|
    user_id, amount = job.arguments
    FailedPayment.create!(user_id: user_id, error: error.message)
    AdminMailer.job_failed(job.job_id, error.message).deliver_later
  end

  def perform(user_id, amount)
    user = User.find(user_id)
    PaymentProcessor.charge(user, amount)
  end
end
```

Inspect and re-drive failures directly via the Solid Queue models:

```ruby
SolidQueue::FailedExecution.count
failed = SolidQueue::FailedExecution.find(id)
failed.retry    # re-enqueue
failed.discard  # delete
SolidQueue::FailedExecution.find_each(&:retry) # retry all (use with care)
```

## Concurrency Controls

`limits_concurrency` replaces the `sidekiq-unique-jobs` gem — it's built in.

```ruby
class DeliverAnnouncementToContactJob < ApplicationJob
  # At most 2 jobs per account run at once; lock auto-expires after 5 min
  limits_concurrency to: 2, key: ->(contact) { contact.account }, duration: 5.minutes

  def perform(contact)
    # ...
  end
end
```

- `to:` — max concurrent jobs sharing the key (default 1)
- `key:` — proc/symbol identifying related jobs
- `duration:` — how long the lock is held (default 3 minutes)
- `group:` — share a limit across different job classes
- `on_conflict:` — `:block` (default, run later) or `:discard`

Idempotent jobs are still the right default — concurrency limits reduce, not
eliminate, double execution:

```ruby
class ProcessOrderJob < ApplicationJob
  def perform(order_id)
    order = Order.find(order_id)
    return if order.processed? # safe to run twice
    order.process!
  end
end
```

## Recurring / Scheduled Jobs

`config/recurring.yml` replaces `sidekiq-cron`. Schedules are parsed by Fugit, so
both cron syntax and natural language work.

```yaml
# config/recurring.yml
production:
  daily_report:
    class: DailyReportJob
    schedule: "every day at 6am"
    queue: default

  cleanup_old_records:
    class: CleanupJob
    schedule: "0 2 * * 0"   # Sunday at 2am (cron)
    queue: low

  refresh_metrics:
    command: "Metrics.refresh!"   # inline command instead of a job class
    schedule: "every 15 minutes"
```

Each task needs `class` (or `command`) plus `schedule`; `args`, `queue`, and
`priority` are optional. The supervisor runs the scheduler unless started with
`--skip-recurring`.

## Testing (Minitest)

Solid Queue uses the standard Active Job test helpers — nothing Solid-specific.

```ruby
# config/environments/test.rb
config.active_job.queue_adapter = :test   # or :inline to run immediately
```

```ruby
# test/jobs/email_sender_job_test.rb
require "test_helper"

class EmailSenderJobTest < ActiveJob::TestCase
  setup { @user = users(:one) }

  test "perform_now sends the welcome email" do
    assert_difference -> { ActionMailer::Base.deliveries.size }, 1 do
      EmailSenderJob.perform_now(@user.id, :welcome)
    end
  end

  test "perform_later enqueues the job" do
    assert_enqueued_with(job: EmailSenderJob, args: [@user.id, :welcome], queue: "default") do
      EmailSenderJob.perform_later(@user.id, :welcome)
    end
  end
end
```

## Monitoring

Use **Mission Control — Jobs**, the official Active Job dashboard, for queues,
retries, failures, and recurring tasks across all Active Job backends:

```ruby
# Gemfile
gem "mission_control-jobs"
```

```ruby
# config/routes.rb
authenticate :user, ->(u) { u.admin? } do
  mount MissionControl::Jobs::Engine, at: "/jobs"
end
```

Or query Solid Queue's tables directly:

```ruby
SolidQueue::Job.count                  # total jobs
SolidQueue::ReadyExecution.count       # waiting to run
SolidQueue::ScheduledExecution.count   # scheduled for later
SolidQueue::FailedExecution.count      # failed (post-retries)
SolidQueue::Process.all                # live workers/dispatchers (heartbeats)
```

## Performance Tips

- Keep jobs small and focused; pass IDs, not objects
- Use exact queue names in `config/queue.yml`, not broad wildcards
- Set realistic `retry_on` attempts and let `discard_on`/`after_discard` handle dead-ends
- Use `limits_concurrency` for jobs that hammer a shared external resource
- Tune `clear_finished_jobs_after` (default 1 day) so the queue tables stay small
- Run the queue in a separate database to isolate its write load from your app
- Scale by adding `processes`/`threads` in `config/queue.yml`, or more `bin/jobs` hosts
- Monitor `SolidQueue::ReadyExecution` depth and per-queue latency
