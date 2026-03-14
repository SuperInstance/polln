# Discord Community Setup Guide

## Server Structure

### Channels Overview

```
📊 SUPERINSTANCE COMMUNITY
│
├── 📢 ANNOUNCEMENTS
│   ├── #announcements        # Official news, releases
│   ├── #changelog            # Version updates
│   └── #events               # Community events, AMAs
│
├── 📚 RESOURCES
│   ├── #documentation        # Docs links, guides
│   ├── #tutorials            # Community tutorials
│   ├── #example-projects     # Showcase projects
│   └── #research-papers      # Relevant papers
│
├── 💬 GENERAL
│   ├── #general              # Off-topic chat
│   ├── #introductions        # New member intros
│   └── #jobs                 # Job postings
│
├── 🛠️ SUPPORT
│   ├── #getting-started      # New user help
│   ├── #sdk-help             # SDK questions
│   ├── #hardware-help        # Hardware issues
│   └── #integration-help     # Integration questions
│
├── 👨‍💻 DEVELOPMENT
│   ├── #development          # Dev discussion
│   ├── #feature-requests     # Propose features
│   ├── #bug-reports          # Report bugs
│   └── #contributing         # Contributing guide
│
└── 🎮 SHOWCASE
    ├── #project-showcase     # Show off projects
    ├── #cartridge-gallery    # Custom cartridges
    └── #adapter-market       # Share adapters
```

## Role Definitions

| Role | Color | Permissions | How to Get |
|------|-------|-------------|------------|
| **@Founder** | Gold | All | Company founders |
| **@Staff** | Purple | Moderate | SuperInstance employees |
| **@Community Lead** | Blue | Moderate | Apply in #meta |
| **@Contributor** | Green | Basic | 1+ merged PR |
| **@Early Adopter** | Orange | Basic | Pre-ordered device |
| **@Verified** | Teal | Basic | Device serial verified |
| **@Member** | Gray | Basic | Default role |

## Welcome Bot Configuration

### Welcome Message

```
🎉 Welcome to SuperInstance, {user}!

You're now part of the edge AI revolution. Here's how to get started:

1️⃣ Read the rules in #rules
2️⃣ Introduce yourself in #introductions
3️⃣ Check out #getting-started for the 5-minute quickstart
4️⃣ Grab your roles in #roles

Quick Links:
📚 Documentation: https://docs.superinstance.ai
💻 GitHub: https://github.com/superinstance-ai
🐦 Twitter: https://twitter.com/SuperInstanceAI

Questions? Just ask in #getting-started!
```

### Auto-Role Bot

Use a bot like Carl-bot or Dyno to add reaction roles:

| Emoji | Role |
|-------|------|
| 🐍 | @Python Developer |
| 🦀 | @Rust Developer |
| ⚡ | @C/C++ Developer |
| 🌐 | @JavaScript Developer |
| 🤖 | @Robotics |
| 🏠 | @Home Assistant |
| 🔬 | @Researcher |
| 🎓 | @Student |

## Community Guidelines (Pinned Message)

```
#rules

📌 COMMUNITY GUIDELINES

1. Be respectful and inclusive
2. No spam or self-promotion without permission
3. Use appropriate channels for your questions
4. Search before asking - your question may be answered
5. Provide code examples and logs when reporting issues
6. No piracy or illegal content discussion
7. English is the primary language

Violation of these rules may result in:
- Warning
- Temporary mute
- Permanent ban

Report issues to @Staff or use /report command

Thank you for making this community awesome! 🚀
```

## Channel-Specific Pinned Messages

### #getting-started
```
📌 QUICK START GUIDE

1. Install: pip install superinstance-sdk
2. Connect: device = Device()
3. Generate: model.generate("Hello!")

Full guide: https://docs.superinstance.ai/getting-started

If you have issues:
- Check USB 3.0 connection
- Run: python -c "from superinstance import Device; print(Device.list_devices())"
- Post error logs below
```

### #sdk-help
```
📌 BEFORE POSTING

✅ Check documentation: https://docs.superinstance.ai/api-reference
✅ Search existing GitHub issues: https://github.com/superinstance-ai/sdk/issues
✅ Include: Python version, SDK version, error message, code snippet

Template:
```
**Python**: 3.10
**SDK**: 0.1.0
**Device**: Micro
**Code**: 
```python
# your code
```
**Error**:
```
# error message
```
```
```

### #hardware-help
```
📌 HARDWARE TROUBLESHOOTING

Before posting:
1. Check LED status (solid green = ready)
2. Try different USB port (USB 3.0 required)
3. Check: lsusb | grep -i super

Include in your post:
- Device model and serial
- LED color/status
- OS and version
- What you were trying to do
```

## Event Templates

### Weekly Office Hours

```
📅 WEEKLY OFFICE HOURS

Join the SuperInstance team for live Q&A!

When: Every Thursday, 2-3 PM PST
Where: Voice channel #office-hours

Agenda:
- 0:00 - 0:10: Announcements
- 0:10 - 0:50: Q&A
- 0:50 - 1:00: Community spotlight

Add to calendar: [link]
```

### Monthly Hackathon Announcement

```
🏆 MONTHLY HACKATHON: {THEME}

Build something amazing with SuperInstance!

📅 Date: {DATE}
⏰ Time: {TIME}
🎁 Prizes: {PRIZES}

Themes:
- 🤖 Autonomous Agents
- 🏠 Smart Home AI
- 📱 Mobile Edge AI
- 🎮 Gaming AI

Register: {LINK}
Submit: {LINK}

Winners announced at end of month!
```

## Moderation Commands

| Command | Usage | Permission |
|---------|-------|------------|
| `/warn @user [reason]` | Warn user | Moderator+ |
| `/mute @user [duration]` | Timeout user | Moderator+ |
| `/kick @user [reason]` | Kick from server | Admin |
| `/ban @user [reason]` | Ban from server | Admin |
| `/slowmode [seconds]` | Set channel slowmode | Moderator+ |
| `/lock` | Lock current channel | Moderator+ |
| `/clear [n]` | Delete last n messages | Moderator+ |

## Analytics & Tracking

Track these metrics weekly:
- Total members
- New members this week
- Active members (7-day)
- Messages per channel
- Average response time in #help channels
- NPS score (monthly survey)

---

**Setup Checklist:**
- [ ] Create server with above structure
- [ ] Set up roles and permissions
- [ ] Configure welcome bot
- [ ] Add reaction roles in #roles
- [ ] Pin guidelines and templates
- [ ] Schedule first office hours
- [ ] Announce server launch
