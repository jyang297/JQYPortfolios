# Portfolio Content Management Guide

## Overview

This Astro portfolio uses **Content Collections** for type-safe, validated content management. All your blog posts and projects are stored as Markdown files with frontmatter metadata.

## Architecture

```
src/
├── content/              # All content lives here
│   ├── config.ts        # Collection schemas & validation
│   ├── blog/            # Blog posts (markdown)
│   ├── projectContents/ # Project descriptions (markdown)
│   └── author/          # Author data (JSON)
├── pages/               # Routes
│   ├── index.astro      # Landing page
│   ├── projects.astro   # Projects listing
│   ├── blog/
│   │   ├── [page].astro       # Individual blog post
│   │   └── [...page].astro    # Blog listing with pagination
│   └── myProjects/
│       └── [slug].astro       # Individual project pages
└── components/          # Reusable components
```

---

## Adding New Blog Posts

### 1. Create a new markdown file

Create a file in `src/content/blog/` with your desired slug as the filename:

```bash
src/content/blog/my-awesome-post.md
```

### 2. Add frontmatter

Every blog post must have this frontmatter structure:

```markdown
---
title: "My Awesome Blog Post"
description: "A brief description for SEO and preview cards"
pubDate: 2025-01-15
isDraft: false
image: "@/assets/blog/my-awesome-post.jpg"
author: "Your Name"
tags: ["web development", "astro", "tutorial"]
---

## Your content starts here

Write your blog post content using standard Markdown syntax.
```

**Note:** The `slug` is auto-generated from the filename for content collections, so you don't need to specify it in frontmatter.

### 3. Frontmatter Fields Explained

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ Yes | Post title displayed in listings and page header |
| `description` | string | ✅ Yes | SEO meta description, shown in cards |
| `pubDate` | date | ✅ Yes | Publication date (YYYY-MM-DD format) |
| `isDraft` | boolean | ✅ Yes | Set to `true` to hide from production |
| `image` | string | ⚠️ Optional | Image path: `"@/assets/blog/image.jpg"` |
| `author` | string | ⚠️ Optional | Author name as string (e.g., "Jane Doe") |
| `tags` | string[] | ⚠️ Optional | Array of tags for categorization |

**Important:** The `slug` field is automatically generated from your filename (e.g., `my-post.md` → slug: `my-post`), so don't include it in frontmatter.

### 4. Image Handling

**Current Setup (Recommended):**
```markdown
---
image: "@/assets/blog/my-post.jpg"
---
```

Place all blog images in `src/assets/blog/`. Astro will automatically optimize these images for production.

**Important:** Do NOT create an `images/` subdirectory inside `src/content/blog/`. Content collection folders should only contain markdown files.

---

## Adding New Projects

### 1. Create a markdown file

```bash
src/content/projectContents/my-project.md
```

### 2. Add frontmatter

```markdown
---
title: "My Awesome Project"
description: "What this project does and why it matters"
date: 2025-01-10
technologies: ["React", "TypeScript", "Tailwind CSS", "Vercel"]
status: "Completed"
draft: false
image: "/images/projects/my-project-thumbnail.jpg"
github: "https://github.com/yourusername/project"
demo: "https://my-project.vercel.app"
featured: true
---

# Project Overview

Detailed description of your project goes here.

## Key Features

- Feature 1
- Feature 2
- Feature 3

## Technical Implementation

Explain your architecture, challenges overcome, etc.
```

### 3. Project Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ Yes | Project name |
| `description` | string | ✅ Yes | Brief summary for cards and SEO |
| `date` | date | ✅ Yes | Project completion/start date |
| `technologies` | string[] | ✅ Yes | Tech stack used (shown as tags) |
| `status` | enum | ✅ Yes | `Planning`, `In Progress`, `Completed`, `Archived` |
| `draft` | boolean | ✅ Yes | Hide from listings if `true` |
| `image` | string | ⚠️ Optional | Thumbnail image URL |
| `github` | URL | ⚠️ Optional | GitHub repository link |
| `demo` | URL | ⚠️ Optional | Live demo URL |
| `featured` | boolean | ⚠️ Optional | Show on homepage if `true` |

---

## Content Workflow

### Writing Content Outside This Project

Since you mentioned writing markdown files outside this project:

**Recommended workflow:**

1. **Write your markdown files anywhere** (Notion, Obsidian, VS Code, etc.)

2. **Copy the completed file** to the appropriate folder:
   - Blog posts → `src/content/blog/`
   - Projects → `src/content/projectContents/`

3. **Ensure frontmatter matches the schema** (see tables above)

4. **Test locally:**
   ```bash
   npm run dev
   ```

5. **Build for production:**
   ```bash
   npm run build
   npm run preview
   ```

### Syncing External Content

If you maintain a separate content repository, consider:

**Option 1: Manual sync**
```bash
# Copy files when ready to publish
cp ~/my-blog-posts/new-post.md src/content/blog/
```

**Option 2: Symbolic link** (advanced)
```bash
# Link external folder to content directory
ln -s ~/my-blog-posts src/content/blog
```

**Option 3: Pre-build script** (recommended for automation)

Create `scripts/sync-content.js`:
```javascript
import fs from 'fs';
import path from 'path';

const SOURCE = '/path/to/your/external/blog';
const DEST = './src/content/blog';

fs.cpSync(SOURCE, DEST, { recursive: true });
console.log('Content synced successfully!');
```

Then update `package.json`:
```json
{
  "scripts": {
    "sync": "node scripts/sync-content.js",
    "build": "npm run sync && astro build"
  }
}
```

---

## Validation & Type Safety

The `config.ts` file provides:

✅ **TypeScript types** - Full autocomplete for frontmatter
✅ **Runtime validation** - Build fails if schema doesn't match
✅ **Image optimization** - Automatic image processing
✅ **Date parsing** - Automatic string-to-Date conversion

### Common Validation Errors

**Error: Missing required field**
```
Error: "title" is required but not provided
```
**Fix:** Add the missing field to frontmatter

**Error: Invalid date format**
```
Error: Expected date, received string
```
**Fix:** Use `YYYY-MM-DD` format: `pubDate: 2025-01-15`

**Error: Invalid enum value**
```
Error: Invalid enum value. Expected 'Planning' | 'In Progress' | 'Completed' | 'Archived'
```
**Fix:** Use exact capitalization for status field

---

## Best Practices

### Content Organization

✅ **Use descriptive slugs:** `advanced-react-patterns` not `post-1`
✅ **Keep frontmatter consistent:** Use the same date format everywhere
✅ **Optimize images:** Keep under 500KB, use WebP/AVIF when possible
✅ **Write meaningful descriptions:** 120-160 characters for SEO

### Markdown Tips

```markdown
<!-- Use proper heading hierarchy -->
# Post Title (H1 - only once)
## Main Sections (H2)
### Subsections (H3)

<!-- Code blocks with syntax highlighting -->
\`\`\`typescript
const example = "Specify language for highlighting";
\`\`\`

<!-- Images with alt text for accessibility -->
![Descriptive alt text](./images/screenshot.png)

<!-- Internal links -->
[See my other post](/blog/other-post)

<!-- External links -->
[Astro Documentation](https://astro.build)
```

---

## Next Steps

### Recommended Improvements

1. **Rename folder for consistency**
   ```bash
   mv src/content/projectContents src/content/projects
   ```
   Then update `config.ts` line 75:
   ```typescript
   projects: projectsCollection, // Changed from "projectContents"
   ```

2. **Add your author profile**
   Edit `src/content/author/default.json` with your information

3. **Create content templates**
   Save template files for quick post creation:
   ```bash
   src/content/blog/_template.md
   src/content/projectContents/_template.md
   ```

4. **Set up RSS feed** (optional)
   ```bash
   npm install @astrojs/rss
   ```
   See: https://docs.astro.build/en/guides/rss/

---

## Troubleshooting

### Build fails with content errors
1. Check `npm run dev` output for specific validation errors
2. Verify all required frontmatter fields exist
3. Ensure dates are in `YYYY-MM-DD` format
4. Check that referenced images exist

### Images not showing
1. Verify image path is correct relative to markdown file
2. Check image file exists at that location
3. Try absolute path from `public/` folder: `/images/file.jpg`

### Type errors in components
1. Run `npm run dev` to regenerate `.astro` types
2. Restart your editor's TypeScript server
3. Check `src/content/config.ts` schema matches your usage

---

## Resources

- **Astro Content Collections:** https://docs.astro.build/en/guides/content-collections/
- **Markdown Syntax:** https://www.markdownguide.org/
- **Zod Schema Validation:** https://zod.dev/
- **Frontmatter Spec:** https://jekyllrb.com/docs/front-matter/
