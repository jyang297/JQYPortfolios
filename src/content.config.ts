import { file, glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";
import { parse as parseToml } from "toml";
import { parse as parseCsv } from "csv-parse/sync";

export const collections = {
  todos: defineCollection({
    loader: async () => {
      const res = await fetch("https://jsonplaceholder.typicode.com/todos");
      const data = await res.json();
      return data.map((todo: any) => ({
        ...todo,
        id: todo.id.toString(),
      }));
    },
    schema: z.object({
      title: z.string(),
      completed: z.boolean(),
    }),
  }),
  posts: defineCollection({
    loader: glob({
      pattern: "src/data/posts/**/*.md",
      // generateId: ({ entry, data }) => data.title as unknown as string,
    }),
    schema: z.object({
      title: z.string(),
      tags: z.array(z.string()),
      pubDate: z.coerce.date(),
      isDraft: z.boolean(),
      canonicalURL: z.string().optional(),
      cover: z.string(),
      coverAlt: z.string(),
    }),
  }),
  team: defineCollection({
    loader: file("src/data/team.json", {
      parser: (text) => JSON.parse(text)["team-1"],
    }),
    schema: z.object({
      name: z.string(),
      role: z.string(),
      email: z.string().email(),
      department: z.enum([
        "Engineering",
        "Software Development",
        "Product Design",
      ]),
    }),
  }),
  cats: defineCollection({
    loader: file("src/data/cats.csv", {
      parser: (text) => parseCsv(text, { columns: true, skipEmptyLines: true }),
    }),
  }),
  toml: defineCollection({
    loader: file("src/data/sample.toml", {
      parser: (text) => parseToml(text).servers,
    }),
  }),
};
