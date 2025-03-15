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

export const collections = { features };
