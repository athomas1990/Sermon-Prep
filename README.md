# Pastor AI Skills

13 AI-powered workflow tools built for pastors. Not prompts. Real multi-step skills that handle the weekly grind so you can focus on ministry.

Built for [Claude Code](https://claude.ai/code). Also works in Claude.ai Projects.

---

## About

I'm Thomas Costello. I've been in pastoral ministry for 20+ years and I run [REACHRIGHT](https://reachrightstudios.com), a church marketing agency. I built these skills for myself because I got tired of writing the same types of content every week from scratch. These are the tools I actually use.

I'm sharing them because pastors deserve better than generic AI prompts. These are workflow tools with pastoral sensitivity built in, not templates you have to heavily rewrite.

---

## The Skills

| Skill | What it does | How often |
|---|---|---|
| **Sermon Prep** | | |
| `/sermon-research` | Deep research on a passage: commentaries, historical context, word studies, thinking prompts. Outputs a formatted PDF. | Weekly |
| `/sermon-brainstorm` | Interactive brainstorm session that produces a clear sermon brief | Weekly |
| `/sermon-series` | Plan a multi-week series with titles, passages, and big ideas | Monthly |
| **Written Communication** | | |
| `/church-email` | Write the weekly church email: subject line, preview text, body | Weekly |
| `/announcement-script` | 60-90 second spoken announcement script for Sunday morning | Weekly |
| `/church-letter` | Letters for any occasion: transitions, updates, celebrations, hard news | As needed |
| **Sermon Repurposing** | | |
| `/small-group-questions` | Discussion questions from Sunday's sermon: observation, interpretation, application | Weekly |
| `/sermon-to-blog` | Turn a sermon into an 800-1200 word blog post (not a transcript) | Weekly |
| `/sermon-to-youtube` | YouTube title, description, tags, thumbnail concept, short-form clip recommendation | Weekly |
| **Social Media** | | |
| `/church-social-post` | Platform-specific posts for Facebook, Instagram, and Twitter | 3-5x/week |
| `/social-media-calendar` | A week or month of content mapped to dates and platforms | Weekly |
| **Pastoral Rhythm** | | |
| `/midweek-devotional` | 200-300 word devotional for email or app: pastoral, personal, brief | Weekly |
| `/meeting-agenda` | Structured agenda with time blocks and discussion questions | Weekly |

---

## Getting Started

### Option 1: Claude Code (Easiest)

Open Claude Code and paste this:

> Install the pastor AI skills from https://github.com/tkcostello/pastor-ai-skills. I want all of them.

That's it. Claude will clone the repo, install the foundation and all the skills for you. If you only want specific skills, just tell it which ones you want.

Once installed, use them by typing `/sermon-research`, `/church-email`, etc.

### Option 2: Manual Install (Claude Code CLI)

If you prefer to do it yourself:

```bash
# Clone the repo
git clone https://github.com/tkcostello/pastor-ai-skills.git

# Copy the foundation (required for all skills)
cp -r pastor-ai-skills/foundation/pastor-foundation ~/.claude/skills/

# Copy any skills you want to use
cp -r pastor-ai-skills/sermon-prep/sermon-research ~/.claude/skills/
cp -r pastor-ai-skills/written-communication/church-email ~/.claude/skills/
cp -r pastor-ai-skills/sermon-repurposing/small-group-questions ~/.claude/skills/
# ... add as many as you need
```

### Option 2: Claude.ai Projects

1. Create a new Project in Claude.ai
2. Open the `SKILL.md` file for the skill you want (you can view them right here on GitHub)
3. Copy the entire contents into your Project's custom instructions
4. For best results, also copy the `pastor-foundation/SKILL.md` content first

---

## Foundation Setup

The first time you use any skill, the foundation will ask for a few details about your church:

- **Church name**
- **Your name**
- **Denomination** (optional, defaults to nondenominational evangelical)
- **Average attendance**
- **Location**
- **Preferred Bible translation** (defaults to NIV)

You set this once. Every skill uses these details to personalize your output so it sounds like it came from someone on your staff, not a robot.

---

## Dependencies

Most skills have zero dependencies. The following skills require a one-time install:

| Skill | Dependency | Install |
|---|---|---|
| `/sermon-research` | reportlab (Python) | `pip install reportlab` |

Claude Code will install this automatically the first time you use the skill. If you prefer to install manually, run the command above.

---

## Philosophy

**These are workflow tools, not prompt templates.** Each skill has a defined process, format rules, and quality standards built in. You don't need to know email marketing best practices or YouTube SEO. The skill knows.

**The foundation layer keeps everything consistent.** Tone, theological sensitivity, and your church's details carry across every skill automatically.

**Sermon prep tools help you research and think. They never write the sermon.** That's between you and the Holy Spirit. The research skill digs into commentaries and context. The brainstorm skill asks you questions. Neither one hands you a manuscript.

**Every output is designed to be ready to use.** Not a rough draft you have to rewrite. Copy, paste, send. If you're rewriting more than 20% of what you get, the skill didn't do its job.

---

## About the Author

**Thomas Costello** is the founder and CEO of [REACHRIGHT](https://reachrightstudios.com) and Executive Pastor at New Hope Hawaii Kai. He's been in ministry for 20+ years, planted a church, led a church through a merger, grew a church from 30 to 150, and built a marketing agency that serves churches across the country.

- [LinkedIn](https://www.linkedin.com/in/tkcostello/)
- [Twitter/X](https://x.com/tkcostello)
- [REACHRIGHT](https://reachrightstudios.com)

---

## License

MIT. Use these however you want.
