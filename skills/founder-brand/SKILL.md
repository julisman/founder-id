---
name: founder-brand
description: >-
  Your brand designer, for Indonesia. Names the business (with the DJKI trademark
  search on PDKI, the .id and .com domain checks and the Instagram, TikTok,
  WhatsApp Business, Shopee and Tokopedia handle checks to run before falling in
  love with a name), checks it reads well in Indonesian and the regional languages
  of the market, writes the voice, a one-line promise and a tagline, and briefs
  the look: colours, type, logo and the first things a customer sees (the sign,
  the cup or package, the marketplace store banner, the WhatsApp profile). Use when
  the user says "name my business", "brand this", "logo", "brand identity", "nama
  usaha", "what should it look like", "tagline", or "brand voice".
argument-hint: "[name ideas, if any]"
---

# founder-brand

A brand is the promise a customer remembers. This skill makes it specific to the
positioning the pack already found, not a mood board of nice colours.

## Step 1: read the brief

`founder/idea.md`, `founder/marketing.md` (the positioning line and the first
audience), `founder/competitors.md` (names and looks to stay clear of), and the
panel's reasons buyers buy (`founder/panel/results.md`). If the positioning is
missing, ask for it or run `/founder-marketing` first.

## Step 2: name candidates

Ten candidates across different styles (descriptive, evocative, invented, the
founder's name, a place, an Indonesian or regional word, an English word if the
segment buys English brands). For each: what it says, how it sounds out loud in
Indonesian, whether it means something unwanted in Javanese, Sundanese or the
language of the target region, how it reads on a sign, a cup or a 32px app icon,
whether buyers can spell it into a search box, and the risk. Then shortlist three
and run the checks the user must finish themselves:

- **Trademark**: search PDKI (pdki-indonesia.dgip.go.id) for the name and close
  spellings in the same Nice classes (for example 30, 43, 35, 3, 25: see
  `${CLAUDE_SKILL_DIR}/../founder-indonesia/reference/permits.md`). Indonesia is
  first-to-file: file with DJKI before launching publicly. If the business will sell
  abroad, add the target country's register.
- **Domain**: whether the .id, .co.id (needs company documents) and .com are free
  (check, do not assume); good alternatives if not.
- **Handles**: Instagram, TikTok, the WhatsApp Business display name, the Shopee and
  Tokopedia/TikTok Shop store names, the Google Business Profile.
- **Confusion**: no name close to a competitor in `founder/competitors.md`.

Say plainly that you can only run public searches, a trademark consultant
(konsultan kekayaan intelektual) confirms it, and nothing is registered until the
user registers it.

## Step 3: voice and promise

- The one-line promise (what the customer can count on, every time).
- A tagline, three options, in the language the buyers use.
- The voice in three adjectives, each with a do and a don't, and a before/after
  rewrite of one line from `founder/pitch.md`. Say how formal it is (santai with
  "kamu", polite with "Anda", or mixed) and keep it the same everywhere, including
  WhatsApp replies.

## Step 4: the look, as a brief

- **Colour**: 2 to 3 core colours with hex values and the job of each, plus the
  contrast check for text on each (WCAG AA at least).
- **Type**: one display and one text face, free or licensed, with where to get
  them. No font the user does not have a licence for.
- **Logo brief**: what it must say, where it must work (a sign, a cup or a
  package, a marketplace thumbnail, a 32px app icon, a WhatsApp profile circle),
  what to avoid. Leave room for the halal logo and the BPOM or PIRT number where
  they will be required. Offer to generate concepts with an image tool if the user
  has one; mark generated concepts as concepts, not a finished logo.
- **The first five touchpoints**: the sign or the marketplace store banner, the
  packaging, the receipt or the order confirmation message, the first TikTok or
  Instagram post, the reply to the first complaint (on Google Maps or the
  marketplace, in public).

## Rules

- Never copy a competitor's name, logo, colours or tagline.
- No fonts, images or icons the user has no right to use.
- No halal, BPOM or SNI marks on designs until the business holds them.
- Not legal advice on trademarks.

## Output

`founder/brand.md`. Next: `/founder-ops` and `/founder-launch`.
