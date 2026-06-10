---
name: rails-expert
description: Rails 8 specialist that optimizes Active Record queries with includes/eager_load, implements Turbo Frames and Turbo Streams for partial page updates and morphing page refreshes, runs background jobs with Solid Queue (the Rails 8 default Active Job adapter), uses Solid Cache for caching and Solid Cable for Action Cable/WebSockets, and writes comprehensive Minitest test suites. Use when building Rails 8 web applications with Hotwire, real-time features, the Solid trifecta, or background job processing. Invoke for Active Record optimization, Turbo Frames/Streams, Solid Queue, Solid Cache, Solid Cable, Minitest.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  adapted-for: "Rails 8 + Solid trifecta (Solid Queue / Solid Cache / Solid Cable)"
  version: "2.0.0"
  domain: backend
  triggers: Rails 8, Ruby on Rails, Hotwire, Turbo Frames, Turbo Streams, Solid Queue, Solid Cache, Solid Cable, Active Record, Minitest, Active Job, morphing
  role: specialist
  scope: implementation
  output-format: code
  related-skills: fullstack-guardian, database-optimizer
---

# Rails Expert (Rails 8 + Solid)

Rails 8 ships a "no PaaS required" stack: the **Solid trifecta** replaces Redis for
most apps. Prefer these defaults over Sidekiq/Redis unless the project already
depends on Redis or has a specific reason not to.

| Concern | Rails 8 default | Replaces |
|---------|-----------------|----------|
| Background jobs | **Solid Queue** (`:solid_queue` Active Job adapter) | Sidekiq / Resque |
| Caching | **Solid Cache** (`:solid_cache_store`) | Redis / Memcached |
| Action Cable / WebSockets | **Solid Cable** (`adapter: solid_cable`) | Redis pub/sub |
| Asset pipeline | Propshaft | Sprockets |
| Deployment | Kamal 2 + Thruster | Capistrano / PaaS |
| Authentication | `bin/rails generate authentication` | Devise (still valid) |

All three Solid stores are database-backed and default to **SQLite** with one
database per concern (`primary`, `queue`, `cache`, `cable`). They work just as
well on PostgreSQL/MySQL by pointing each at its own database.

## Core Workflow

1. **Analyze requirements** — Identify models, routes, real-time needs, background jobs, cache hot paths
2. **Scaffold resources** — `bin/rails generate model User name:string email:string`, `bin/rails generate controller Users`
3. **Run migrations** — `bin/rails db:migrate` (or `bin/rails db:prepare` to create the Solid databases too) and verify schema with `bin/rails db:schema:dump`
   - If migration fails: inspect `db/schema.rb` for conflicts, rollback with `bin/rails db:rollback`, fix and retry
4. **Implement** — Write controllers, models, add Hotwire (see Reference Guide below)
5. **Validate** — `bin/rails test` (and `bin/rails test:system`) must pass; `bin/rubocop` (rubocop-rails-omakase ships by default) for style; `bin/brakeman` for security
   - If tests fail: read the failure output, fix the failing test, re-run the single file/line (`bin/rails test path:line`) for a fast loop
   - If N+1 queries surface during review: add `includes`/`eager_load` (see Common Patterns) and re-run the tests
6. **Optimize** — Audit for N+1 queries, add missing indexes, add Solid Cache fragment/low-level caching

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Hotwire/Turbo | `references/hotwire-turbo.md` | Turbo Frames, Streams, morphing refreshes, Stimulus, Solid Cable broadcasting |
| Active Record | `references/active-record.md` | Models, associations, queries, performance, multi-database |
| Background Jobs | `references/background-jobs.md` | Solid Queue setup, job design, queues, recurring jobs, concurrency, error handling |
| Testing | `references/minitest-testing.md` | Model/integration/system/job tests, fixtures |
| API Development | `references/api-development.md` | API-only mode, serialization, authentication, native rate limiting |

## Common Patterns

### N+1 Prevention with includes/eager_load

```ruby
# BAD — triggers N+1
posts = Post.all
posts.each { |post| puts post.author.name }

# GOOD — eager load association
posts = Post.includes(:author).all
posts.each { |post| puts post.author.name }

# GOOD — eager_load forces a JOIN (useful when filtering on association)
posts = Post.eager_load(:author).where(authors: { verified: true })
```

### Turbo Frame Setup (partial page update)

```erb
<%# app/views/posts/index.html.erb %>
<%= turbo_frame_tag "posts" do %>
  <%= render @posts %>
  <%= link_to "Load More", posts_path(page: @next_page) %>
<% end %>

<%# app/views/posts/_post.html.erb %>
<%= turbo_frame_tag dom_id(post) do %>
  <h2><%= post.title %></h2>
  <%= link_to "Edit", edit_post_path(post) %>
<% end %>
```

```ruby
# app/controllers/posts_controller.rb
def index
  @posts = Post.includes(:author).page(params[:page])
  @next_page = @posts.next_page
end
```

### Solid Queue Job Template (Active Job)

Solid Queue is a pure Active Job backend — there is no `sidekiq_options`. Retries,
discards, and error handling all use the standard Active Job API.

```ruby
# app/jobs/send_welcome_email_job.rb
class SendWelcomeEmailJob < ApplicationJob
  queue_as :default

  # Active Job handles retries; Solid Queue executes them
  retry_on Net::OpenTimeout, wait: :polynomially_longer, attempts: 5

  # Record is gone — no point retrying, so drop the job
  discard_on ActiveRecord::RecordNotFound

  def perform(user_id)
    user = User.find(user_id)
    UserMailer.welcome(user).deliver_now
  end
end

# Enqueue from controller or model callback
SendWelcomeEmailJob.perform_later(user.id)

# Bulk enqueue (single round-trip)
SendWelcomeEmailJob.perform_all_later(user_ids.map { |id| SendWelcomeEmailJob.new(id) })
```

### Strong Parameters (controller template)

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  before_action :set_post, only: %i[show edit update destroy]

  def create
    @post = Post.new(post_params)
    if @post.save
      redirect_to @post, notice: "Post created."
    else
      render :new, status: :unprocessable_entity
    end
  end

  private

  def set_post
    @post = Post.find(params[:id])
  end

  def post_params
    params.expect(post: [:title, :body, :published_at]) # Rails 8 params.expect
  end
end
```

> Rails 8 adds `params.expect`, which raises `ParameterMissing`/`400` (not `500`) on
> malformed nested params. `params.require(:post).permit(...)` still works.

## Constraints

### MUST DO
- Prevent N+1 queries with `includes`/`eager_load` on every collection query involving associations
- Write comprehensive Minitest tests targeting >95% coverage
- Use service objects for complex business logic; keep controllers thin
- Add database indexes for every column used in `WHERE`, `ORDER BY`, or `JOIN`
- Offload slow operations to **Solid Queue** with `perform_later` — never run them synchronously in a request cycle
- Pass record **IDs** (not objects) to jobs so Active Job serialization stays cheap and safe

### MUST NOT DO
- Skip migrations for schema changes
- Use raw SQL without sanitization (`sanitize_sql` or parameterized queries only)
- Use `sidekiq_options`/Redis-specific APIs on a Solid Queue app — use Active Job + Solid Queue features (`limits_concurrency`, `config/recurring.yml`) instead
- Expose internal IDs in URLs without consideration

## Output Templates

When implementing Rails features, provide:
1. Migration file (if schema changes needed)
2. Model file with associations and validations
3. Controller with RESTful actions and strong parameters
4. View files or Hotwire setup
5. Minitest files for models and requests (under `test/`)
6. Brief explanation of architectural decisions

---

Adapted for Rails 8 + the Solid trifecta from the original
[`rails-expert`](https://github.com/Jeffallan/claude-skills/tree/main/skills/rails-expert)
skill by [@Jeffallan](https://github.com/Jeffallan) (MIT).
