/**
 * Content Collections Configuration
 *
 * This file defines the schema and validation rules for your content collections.
 * Astro will use these schemas to provide TypeScript types and validate frontmatter.
 *
 * @see https://docs.astro.build/en/guides/content-collections/
 */

import { defineCollection, reference, z } from 'astro:content';

/**
 * Author Collection Schema
 * Defines the structure for author information referenced in blog posts
 */
const authorCollection = defineCollection({
  type: 'data',
  schema: z.object({
    name: z.string(),
    bio: z.string().optional(),
    avatar: z.string().optional(),
    twitter: z.string().optional(),
    github: z.string().optional(),
  }),
});

/**
 * Blog Collection Schema
 * Defines the structure for blog post markdown files in src/content/blog/
 *
 * Images are now stored in src/assets/blog/ and referenced as "@/assets/blog/filename.jpg"
 * This enables Astro's automatic image optimization
 */
const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    // slug is auto-generated from filename for type:'content' collections
    description: z.string(),
    pubDate: z.coerce.date(), // Automatically converts strings to Date objects
    isDraft: z.boolean().default(false),
    // Accept string paths to images in assets folder (Astro will optimize these)
    image: z.string().optional(),
    // Author can be either a string name or a reference to author collection
    author: z.union([z.string(), reference('author')]).optional(),
    tags: z.array(z.string()).optional(),
  }),
});

/**
 * AI Agents Collection
 * Markdown files in src/content/agents/
 */
const agentsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    technologies: z.array(z.string()).optional(),
    status: z.enum(['Planning', 'In Progress', 'Completed', 'Archived']).default('In Progress'),
    draft: z.boolean().default(false),
    github: z.string().url().optional(),
    demo: z.string().url().optional(),
  }),
});

/**
 * ML Projects Collection
 * Markdown files in src/content/ml/
 */
const mlCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    technologies: z.array(z.string()).optional(),
    status: z.enum(['Planning', 'In Progress', 'Completed', 'Archived']).default('In Progress'),
    draft: z.boolean().default(false),
    github: z.string().url().optional(),
    demo: z.string().url().optional(),
  }),
});

/**
 * Photo Albums Collection
 * Markdown files in src/content/albums/
 */
const albumsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    image: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

/**
 * Export all collections
 * Collection names must match the folder names or file names (for data collections) in src/content/
 */
export const collections = {
  author: authorCollection,
  blog: blogCollection,
  agents: agentsCollection,
  ml: mlCollection,
  albums: albumsCollection,
};
