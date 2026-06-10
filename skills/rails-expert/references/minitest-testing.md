# Minitest Testing (Rails default)

Rails 8 ships with **Minitest** and **fixtures** out of the box — no extra gems
required. Tests live under `test/`, run with `bin/rails test` (and
`bin/rails test:system` for browser tests), and run in parallel by default.

## Setup

The generated `test/test_helper.rb` already wires everything up:

```ruby
# test/test_helper.rb
ENV["RAILS_ENV"] ||= "test"
require_relative "../config/environment"
require "rails/test_help"

module ActiveSupport
  class TestCase
    # Run tests in parallel across CPU cores
    parallelize(workers: :number_of_processors)

    # Load all fixtures into the test database for every test
    fixtures :all

    # Add app-wide test helpers here
  end
end
```

Each test runs inside a transaction that rolls back afterward, so the database
stays clean between tests without any extra setup.

Run tests:

```bash
bin/rails test                       # all non-system tests
bin/rails test test/models           # a directory
bin/rails test test/models/user_test.rb:42   # a single test by line
bin/rails test:system                # browser/system tests
bin/rails test:all                   # everything, including system tests
```

## Fixtures

Fixtures are the Rails default test data — YAML files under `test/fixtures/`,
one per table.

```yaml
# test/fixtures/users.yml
one:
  email: alice@example.com
  username: alice
  active: true

admin:
  email: admin@example.com
  username: admin
  active: true
  role: admin
```

```yaml
# test/fixtures/posts.yml
welcome:
  title: "Hello World"
  body: "First post"
  published: true
  user: one        # references users(:one) by association name
```

Reference them in tests with the table-name helper: `users(:one)`, `posts(:welcome)`.

> Prefer FactoryBot? Add `factory_bot_rails`, drop your factories in
> `test/factories/`, and `include FactoryBot::Syntax::Methods` in the test case.
> Fixtures are the default and the fastest path, so reach for factories only when
> you need them.

## Model Tests

```ruby
# test/models/user_test.rb
require "test_helper"

class UserTest < ActiveSupport::TestCase
  test "is valid with required attributes" do
    user = User.new(email: "new@example.com", username: "newbie")
    assert user.valid?
  end

  test "requires an email" do
    user = User.new(username: "noemail")
    assert_not user.valid?
    assert_includes user.errors[:email], "can't be blank"
  end

  test "requires a unique email" do
    User.create!(email: "dup@example.com", username: "first")
    dup = User.new(email: "dup@example.com", username: "second")
    assert_not dup.valid?
  end

  test "normalizes email before save" do
    user = User.create!(email: "USER@EXAMPLE.COM", username: "casing")
    assert_equal "user@example.com", user.reload.email
  end

  test "active scope returns only active users" do
    assert_includes User.active, users(:one)
  end

  test "destroys dependent posts" do
    user = users(:one)
    assert_difference("Post.count", -user.posts.count) do
      user.destroy
    end
  end
end
```

## Integration / Controller Tests

`ActionDispatch::IntegrationTest` exercises full request/response cycles through
the router — the recommended way to test controllers in modern Rails.

```ruby
# test/integration/posts_test.rb
require "test_helper"

class PostsTest < ActionDispatch::IntegrationTest
  setup do
    @user = users(:one)
    sign_in_as(@user) # see "Authentication in tests" below
  end

  test "index renders successfully" do
    get posts_url
    assert_response :success
  end

  test "show renders successfully" do
    get post_url(posts(:welcome))
    assert_response :success
  end

  test "creates a post with valid params" do
    assert_difference("Post.count", 1) do
      post posts_url, params: { post: { title: "Test Post", body: "Content" } }
    end
    assert_redirected_to post_url(Post.last)
  end

  test "does not create a post with invalid params" do
    assert_no_difference("Post.count") do
      post posts_url, params: { post: { title: "", body: "" } }
    end
    assert_response :unprocessable_entity
  end

  test "updates a post" do
    post_record = posts(:welcome)
    patch post_url(post_record), params: { post: { title: "Updated Title" } }
    assert_redirected_to post_url(post_record)
    assert_equal "Updated Title", post_record.reload.title
  end

  test "destroys a post" do
    assert_difference("Post.count", -1) do
      delete post_url(posts(:welcome))
    end
  end
end
```

### Authentication in tests

With Rails 8's generated authentication, sign in by posting to the session route
and reusing the cookie. A small helper keeps tests readable:

```ruby
# test/test_helper.rb (inside ActiveSupport::TestCase or a dedicated module)
module SignInHelper
  def sign_in_as(user, password: "password")
    post session_url, params: { email_address: user.email_address, password: password }
  end
end

class ActionDispatch::IntegrationTest
  include SignInHelper
end
```

## System Tests (browser)

System tests use Capybara + Selenium and ship by default
(`ApplicationSystemTestCase` is generated under `test/system/`).

```ruby
# test/application_system_test_case.rb
require "test_helper"

class ApplicationSystemTestCase < ActionDispatch::SystemTestCase
  driven_by :selenium, using: :headless_chrome, screen_size: [1400, 1400]
end
```

```ruby
# test/system/posts_test.rb
require "application_system_test_case"

class PostsTest < ApplicationSystemTestCase
  setup { @user = users(:one) }

  test "creating a post" do
    sign_in_as(@user)
    visit new_post_url

    fill_in "Title", with: "My New Post"
    fill_in "Body",  with: "This is the content"
    click_on "Create Post"

    assert_text "Post was successfully created"
    assert_text "My New Post"
  end

  test "editing a post via Turbo Frame" do
    sign_in_as(@user)
    visit post_url(posts(:welcome))

    click_on "Edit"
    fill_in "Title", with: "Updated Title"
    click_on "Update Post"

    assert_text "Updated Title"
    assert_no_selector "form"
  end
end
```

## Testing Jobs (Solid Queue)

Solid Queue is a plain Active Job backend, so use Rails' Active Job test helpers.
Set the test adapter (Rails defaults the test env to `:test`):

```ruby
# config/environments/test.rb
config.active_job.queue_adapter = :test   # or :inline to run jobs immediately
```

```ruby
# test/jobs/email_sender_job_test.rb
require "test_helper"

class EmailSenderJobTest < ActiveJob::TestCase
  setup { @user = users(:one) }

  test "perform_now sends an email" do
    assert_difference -> { ActionMailer::Base.deliveries.size }, 1 do
      EmailSenderJob.perform_now(@user.id, :welcome)
    end
  end

  test "perform_later enqueues the job" do
    assert_enqueued_with(job: EmailSenderJob, args: [@user.id, :welcome], queue: "default") do
      EmailSenderJob.perform_later(@user.id, :welcome)
    end
  end

  test "runs enqueued jobs in a block" do
    perform_enqueued_jobs do
      EmailSenderJob.perform_later(@user.id, :welcome)
    end
    assert_equal 1, ActionMailer::Base.deliveries.size
  end
end
```

Assert that a controller action enqueues a job:

```ruby
class CommentsTest < ActionDispatch::IntegrationTest
  include ActiveJob::TestHelper

  test "creating a comment enqueues a notification" do
    assert_enqueued_jobs 1, only: NotifyAuthorJob do
      post post_comments_url(posts(:welcome)), params: { comment: { body: "Nice!" } }
    end
  end
end
```

## Testing Mailers

```ruby
# test/mailers/user_mailer_test.rb
require "test_helper"

class UserMailerTest < ActionMailer::TestCase
  test "welcome email" do
    user = users(:one)
    mail = UserMailer.welcome(user)

    assert_equal "Welcome to Our App", mail.subject
    assert_equal [user.email], mail.to
    assert_equal ["noreply@example.com"], mail.from
    assert_match user.username, mail.body.encoded
  end
end
```

## Common Assertions

```ruby
assert        value
assert_not    value
assert_equal  expected, actual
assert_nil    value
assert_includes collection, member
assert_match  /regex/, string
assert_difference("Model.count", 1) { ... }
assert_no_difference("Model.count") { ... }
assert_response :success            # :redirect, :not_found, :unprocessable_entity
assert_redirected_to some_url
assert_changes -> { obj.status }, from: "draft", to: "published" { ... }
assert_enqueued_with(job: MyJob, args: [...])
```

## Best Practices

- Lean on fixtures first; add FactoryBot only when fixtures get unwieldy
- One behavior per test; give tests descriptive names
- Use `setup` blocks for shared arrangement
- Test edge cases and error conditions, not just the happy path
- Use `travel_to`/`freeze_time` for time-dependent logic
- Stub external HTTP with WebMock/VCR — never hit real services in tests
- Keep system tests focused on critical user flows; they're slower than the rest
- Track coverage with SimpleCov (`gem "simplecov", require: false`) started at the top of `test_helper.rb`
- Run `bin/rails test` and `bin/rails test:system` in CI; let parallelization keep them fast
