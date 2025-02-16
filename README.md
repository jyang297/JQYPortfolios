# Rewrites, redirects, and preventing.

1. Rewrite `/about` to show `/` instead.
   
2. Use a global config to redirect `/about` to `/`.

3. Prevent `/about` from being built.

# Creating routes
1. Add a `/posts` page that shows all link to all posts in your `posts` content collection.

2. Create a dynamic route for all posts under the `/posts` directory using SSG mode.

3. Create a paginated `/posts` route with two posts per page and prev and next buttons showing when available.

# SSR vs SSG

1. Enable SSR and prerender the homepage only.

2. With SSR enabled, prerender every page except for the homepage.