# API Development

## API-Only Rails Application

```ruby
# Generate API-only app
rails new myapp --api

# config/application.rb
module MyApp
  class Application < Rails::Application
    config.api_only = true
    config.load_defaults 8.0
  end
end

# app/controllers/application_controller.rb
class ApplicationController < ActionController::API
  include ActionController::HttpAuthentication::Token::ControllerMethods

  before_action :authenticate

  rescue_from ActiveRecord::RecordNotFound, with: :not_found
  rescue_from ActiveRecord::RecordInvalid, with: :unprocessable_entity

  private

  def authenticate
    authenticate_token || render_unauthorized
  end

  def authenticate_token
    authenticate_with_http_token do |token, options|
      @current_user = User.find_by(api_token: token)
    end
  end

  def render_unauthorized
    render json: { error: 'Unauthorized' }, status: :unauthorized
  end

  def not_found
    render json: { error: 'Not found' }, status: :not_found
  end

  def unprocessable_entity(exception)
    render json: { errors: exception.record.errors }, status: :unprocessable_entity
  end
end
```

## RESTful API Controller

```ruby
# app/controllers/api/v1/posts_controller.rb
module Api
  module V1
    class PostsController < ApplicationController
      before_action :set_post, only: [:show, :update, :destroy]

      # GET /api/v1/posts
      def index
        @posts = Post.includes(:user)
                    .page(params[:page])
                    .per(params[:per_page] || 20)

        render json: @posts, meta: pagination_meta(@posts)
      end

      # GET /api/v1/posts/:id
      def show
        render json: @post, include: [:user, :comments]
      end

      # POST /api/v1/posts
      def create
        @post = current_user.posts.build(post_params)

        if @post.save
          render json: @post, status: :created, location: api_v1_post_url(@post)
        else
          render json: { errors: @post.errors }, status: :unprocessable_entity
        end
      end

      # PATCH/PUT /api/v1/posts/:id
      def update
        if @post.update(post_params)
          render json: @post
        else
          render json: { errors: @post.errors }, status: :unprocessable_entity
        end
      end

      # DELETE /api/v1/posts/:id
      def destroy
        @post.destroy
        head :no_content
      end

      private

      def set_post
        @post = Post.find(params[:id])
      end

      def post_params
        params.expect(post: [:title, :body, :published]) # Rails 8 params.expect
      end

      def pagination_meta(collection)
        {
          current_page: collection.current_page,
          total_pages: collection.total_pages,
          total_count: collection.total_count
        }
      end
    end
  end
end
```

## Serialization

For simple payloads, Rails' built-in Jbuilder (default in full apps) or plain
`render json:` with `as_json` options is usually enough. For richer needs reach
for a serializer gem (`active_model_serializers`, `alba`, or `jsonapi-serializer`).

```ruby
# app/serializers/post_serializer.rb (active_model_serializers)
class PostSerializer < ActiveModel::Serializer
  attributes :id, :title, :body, :published, :created_at

  belongs_to :user
  has_many :comments

  attribute :draft_content, if: :current_user_is_author?

  def published_date
    object.created_at.strftime("%Y-%m-%d")
  end

  private

  def current_user_is_author?
    current_user == object.user
  end
end
```

```ruby
# Jbuilder alternative — app/views/api/v1/posts/show.json.jbuilder
json.extract! @post, :id, :title, :body, :published, :created_at
json.user do
  json.extract! @post.user, :id, :username
end
json.comments @post.comments, :id, :body
```

## Authentication

### Rails 8 built-in authentication (sessions / web)

Rails 8 generates a complete password-based auth system — no Devise required:

```bash
bin/rails generate authentication
```

This creates a `User` with `has_secure_password`, a `Session` model, an
`Authentication` concern (`authenticate_by`, `Current.user`, `require_authentication`),
and password-reset mailers. Use it for first-party/web clients; layer token or JWT
auth on top for third-party API clients.

### JWT authentication (token-based API clients)

```ruby
# Gemfile
gem 'jwt'

# app/lib/json_web_token.rb
class JsonWebToken
  SECRET_KEY = Rails.application.credentials.secret_key_base

  def self.encode(payload, exp = 24.hours.from_now)
    payload[:exp] = exp.to_i
    JWT.encode(payload, SECRET_KEY)
  end

  def self.decode(token)
    decoded = JWT.decode(token, SECRET_KEY)[0]
    HashWithIndifferentAccess.new(decoded)
  rescue JWT::DecodeError
    nil
  end
end

# app/controllers/api/v1/authentication_controller.rb
module Api
  module V1
    class AuthenticationController < ApplicationController
      skip_before_action :authenticate, only: [:create]

      # POST /api/v1/auth/login
      def create
        user = User.authenticate_by(email: params[:email], password: params[:password])

        if user
          token = JsonWebToken.encode(user_id: user.id)
          render json: { token: token, user: { id: user.id, email: user.email } }
        else
          render json: { error: 'Invalid credentials' }, status: :unauthorized
        end
      end
    end
  end
end

# app/controllers/application_controller.rb
class ApplicationController < ActionController::API
  before_action :authenticate_request

  attr_reader :current_user

  private

  def authenticate_request
    header = request.headers['Authorization']
    token = header.split(' ').last if header

    decoded = JsonWebToken.decode(token)
    @current_user = User.find(decoded[:user_id]) if decoded

    render json: { error: 'Unauthorized' }, status: :unauthorized unless @current_user
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Unauthorized' }, status: :unauthorized
  end
end
```

> `User.authenticate_by` (Rails 7.1+) checks the password in constant time even when
> the email doesn't exist, avoiding timing-based user enumeration.

## API Versioning

```ruby
# config/routes.rb
Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      resources :posts
      resources :users

      post '/auth/login', to: 'authentication#create'
    end

    namespace :v2 do
      resources :posts
    end
  end
end
```

## Rate Limiting

### Rails 8 native rate limiting (recommended)

Rails 8 ships `rate_limit` in Action Controller, backed by the cache store — so on
a Solid stack it rides on **Solid Cache** with no extra gem or Redis:

```ruby
class Api::V1::AuthenticationController < ApplicationController
  # 5 login attempts per 20 seconds per client IP
  rate_limit to: 5, within: 20.seconds, only: :create,
             with: -> { render json: { error: "Too many attempts" }, status: :too_many_requests }
end

class Api::V1::PostsController < ApplicationController
  # Scope the throttle key however you like (here: API token)
  rate_limit to: 1000, within: 1.hour, by: -> { request.headers["Authorization"] }
end
```

### rack-attack (alternative / global throttling)

Use rack-attack when you need IP blocklists or middleware-level throttling across
the whole app:

```ruby
# Gemfile
gem 'rack-attack'

# config/initializers/rack_attack.rb
class Rack::Attack
  throttle('req/ip', limit: 300, period: 5.minutes) { |req| req.ip }

  blocklist('block bad IPs') do |req|
    BadIpList.include?(req.ip)
  end
end

# config/application.rb
config.middleware.use Rack::Attack
```

## CORS Configuration

```ruby
# Gemfile
gem 'rack-cors'

# config/initializers/cors.rb
Rails.application.config.middleware.insert_before 0, Rack::Cors do
  allow do
    origins 'localhost:3000', 'example.com'

    resource '*',
      headers: :any,
      methods: [:get, :post, :put, :patch, :delete, :options, :head],
      credentials: true
  end
end
```

## Testing & Documenting the API (Minitest)

Cover API endpoints with integration tests. They double as living documentation;
keep an OpenAPI spec (hand-written or generated) alongside if you publish the API.

```ruby
# test/integration/api/v1/posts_test.rb
require "test_helper"

class Api::V1::PostsTest < ActionDispatch::IntegrationTest
  setup do
    @user = users(:one)
    @headers = { "Authorization" => "Bearer #{JsonWebToken.encode(user_id: @user.id)}" }
  end

  test "lists posts" do
    get api_v1_posts_url, headers: @headers
    assert_response :success
    assert_kind_of Array, response.parsed_body
  end

  test "creates a post" do
    assert_difference("Post.count", 1) do
      post api_v1_posts_url,
           params: { post: { title: "Test", body: "Content" } },
           headers: @headers,
           as: :json
    end
    assert_response :created
    assert_equal "Test", response.parsed_body["title"]
  end

  test "rejects unauthenticated requests" do
    get api_v1_posts_url
    assert_response :unauthorized
  end
end
```

## Error Handling

```ruby
# app/controllers/concerns/error_handler.rb
module ErrorHandler
  extend ActiveSupport::Concern

  included do
    rescue_from ActiveRecord::RecordNotFound, with: :not_found
    rescue_from ActiveRecord::RecordInvalid, with: :unprocessable_entity
    rescue_from ActionController::ParameterMissing, with: :bad_request
  end

  private

  def not_found(exception)
    render json: { error: exception.message }, status: :not_found
  end

  def unprocessable_entity(exception)
    render json: { errors: exception.record.errors.full_messages },
           status: :unprocessable_entity
  end

  def bad_request(exception)
    render json: { error: exception.message }, status: :bad_request
  end
end
```

## Best Practices

- Use semantic versioning for API versions
- Return proper HTTP status codes
- Include pagination for list endpoints
- Use JSON:API or similar standard format
- Document the API with OpenAPI/Swagger
- Rate-limit with the built-in `rate_limit` (Solid Cache–backed) before adding gems
- Use HTTPS in production
- Validate and sanitize all inputs with `params.expect`/strong parameters
- Provide helpful error messages
