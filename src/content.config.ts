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
 * Projects Collection (Featured Projects)
 * This is a data collection from projects.yaml
 * Used for the "Featured Projects" section on the homepage
 */
const projectsCollection = defineCollection({
  type: 'data',
  schema: ({ image }) => z.object({
    id: z.number(),
    title: z.string(),
    image: image(), // Astro optimized image
    href: z.string(), // URL to project page or external link
  }),
});

/**
 * Project Contents Collection (Full Project Pages)
 * Markdown files in projectContents/ folder
 * Used for detailed project pages at /myProjects/[slug]
 */
const projectContentsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    technologies: z.array(z.string()),
    status: z.enum(['Planning', 'In Progress', 'Completed', 'Archived']).default('In Progress'),
    draft: z.boolean().default(false),
    image: z.string().optional(),
    github: z.string().url().optional(),
    demo: z.string().url().optional(),
    featured: z.boolean().default(false),
  }),
});

/**
 * Export all collections
 * Collection names must match the folder names or file names (for data collections) in src/content/
 */
export const collections = {
  author: authorCollection,
  blog: blogCollection,
  projects: projectsCollection, // From projects.yaml - featured projects
  projectContents: projectContentsCollection, // From projectContents/ - full project pages
};
