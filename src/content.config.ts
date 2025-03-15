import { file } from "astro/loaders";
import { defineCollection, z } from "astro:content";

const features = defineCollection({
  loader: file("src/content/features.json"),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    icon: z.string(),
  }),
});

const projects = defineCollection({
  loader: file("src/content/projects.yaml"),
  schema: ({ image }) =>
    z.object({
      title: z.string().max(65),
      href: z.string().url(),
      image: image(),
    }),
});

export const collections = { features, projects };
