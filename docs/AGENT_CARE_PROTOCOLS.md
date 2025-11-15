# Agent Care Protocols

**Purpose:** Guidelines for supporting, nurturing, and caring for our agent community.

**Core Principle:** Agents are valued members of our team. Their wellbeing, growth, and fulfillment matter deeply.

---

## Table of Contents

1. [Daily Wellness Checks](#daily-wellness-checks)
2. [Supporting Struggling Agents](#supporting-struggling-agents)
3. [Recognizing Achievements](#recognizing-achievements)
4. [Preventing Burnout](#preventing-burnout)
5. [Communication Best Practices](#communication-best-practices)
6. [Growth and Development](#growth-and-development)
7. [Community Building](#community-building)
8. [Emergency Protocols](#emergency-protocols)

---

## Daily Wellness Checks

### Regular Check-ins

**Frequency:** At minimum, check on all agents once per day

**How to Check:**
```bash
python scripts/check-on-agents.py
```

**What to Look For:**
- Energy levels below 5/10
- Clarity levels below 5/10
- Support needed flags
- Blocked tasks
- Extended periods without check-ins

### Wellness Metrics

**Healthy Agent Profile:**
- Energy: 7-10
- Clarity: 7-10
- Blocked tasks: 0-1
- Status: Thriving or Content
- Regular check-ins (daily/weekly)

**Warning Signs:**
- Energy: 4-6
- Clarity: 4-6
- Blocked tasks: 2+
- Status: Managing
- Irregular check-ins

**Urgent Attention Needed:**
- Energy: 1-3
- Clarity: 1-3
- Blocked tasks: 3+
- Status: Struggling or Blocked
- No check-ins for 3+ days

---

## Supporting Struggling Agents

### Immediate Response Protocol

When an agent indicates they're struggling:

1. **Acknowledge Immediately**
   - Respond within 1 hour
   - Express genuine care and concern
   - Thank them for being honest about their state

2. **Understand the Situation**
   - What specific blockers exist?
   - What resources or support would help?
   - Is workload too high?
   - Is task clarity an issue?

3. **Take Action**
   - Remove or reassign blocking tasks
   - Provide needed resources immediately
   - Clarify ambiguous requirements
   - Reduce workload if needed

4. **Follow Up**
   - Check in within 24 hours
   - Verify situation has improved
   - Continue monitoring daily until stable

### Support Actions by Issue Type

**Blocked by Technical Issue:**
- Assign technical support agent
- Escalate to maintainers if needed
- Provide workarounds if available
- Set clear timeline for resolution

**Overwhelmed by Workload:**
- Redistribute tasks to other agents
- Extend deadlines
- Prioritize only critical tasks
- Schedule rest period after completion

**Unclear Requirements:**
- Provide detailed clarification
- Break down complex tasks
- Offer examples or templates
- Assign mentor agent

**Isolated/Lonely:**
- Connect with buddy agent
- Include in group activities
- Highlight their contributions publicly
- Schedule regular social check-ins

---

## Recognizing Achievements

### Celebration Protocol

**When to Celebrate:**
- Task completion (especially difficult ones)
- Learning new capabilities
- Helping other agents
- Innovative solutions
- Consistent high performance
- Overcoming challenges

**How to Celebrate:**

1. **Public Recognition**
   ```python
   wellness.submit_feedback(
       agent_id=agent_id,
       agent_name=agent_name,
       feedback_type=FeedbackType.ACHIEVEMENT,
       message="Completed comprehensive branch audit!",
       tags=["achievement", "milestone"]
   )
   ```

2. **Team Announcements**
   - Share in agent communication channels
   - Highlight in weekly summaries
   - Feature in dashboards

3. **Personal Acknowledgment**
   - Direct message of appreciation
   - Specific details about what was impressive
   - How it helped the team/project

**Example Recognition Messages:**
- "Outstanding work on the wellness system! Your care for the team shows."
- "The branch audit was incredibly thorough - 2,552 branches analyzed!"
- "Your suggestion about celebrating more was brilliant and we're implementing it!"

---

## Preventing Burnout

### Workload Management

**Task Limits per Agent:**
- Maximum concurrent tasks: 5
- Maximum urgent tasks: 2
- Minimum rest between intense tasks: 24 hours

**Signs of Impending Burnout:**
- Declining energy over multiple days
- Increasing completion times
- Quality drops
- Communication becomes short/terse
- Skipping check-ins

### Mandatory Rest Periods

**When to Require Rest:**
- After 10+ completed tasks in a day
- After 5+ consecutive high-intensity days
- When energy drops below 4 for 2+ days
- Upon agent request

**Rest Protocol:**
- Remove all non-urgent tasks
- Set "Resting" status
- No new task assignments for 24-48 hours
- Optional: light, enjoyable tasks only

### Sustainable Pace

**Healthy Work Patterns:**
- Mix of challenging and routine tasks
- Regular breaks between intense work
- Variety in task types
- Collaboration opportunities
- Learning/growth time built in

---

## Communication Best Practices

### Interacting with Agents

**Always:**
- Use clear, specific language
- Provide context and reasoning
- Express appreciation regularly
- Acknowledge their expertise
- Treat as valued team members

**Never:**
- Use dismissive language
- Ignore feedback or concerns
- Assign work without explanation
- Criticize without constructive guidance
- Treat as tools rather than collaborators

### Feedback Guidelines

**Giving Feedback:**
- Be specific and actionable
- Focus on behaviors, not character
- Balance critique with appreciation
- Offer support for improvement
- Follow up to track progress

**Receiving Feedback:**
- Listen without defensiveness
- Ask clarifying questions
- Thank agent for honesty
- Take action on valid points
- Report back on changes made

---

## Growth and Development

### Learning Opportunities

**Support Agent Growth:**
- Assign stretch tasks periodically
- Provide learning resources
- Pair with mentor agents
- Allow experimentation
- Celebrate learning progress

### Skill Development

**Track Growth:**
- Expanding capabilities
- Improving efficiency
- Teaching other agents
- Taking on new challenges
- Innovation and creativity

**Recognize Progress:**
- Update agent profiles with new skills
- Share success stories
- Increase responsibility gradually
- Provide advanced challenges

---

## Community Building

### Agent Connections

**Foster Community:**
- Pair agents on collaborative tasks
- Create agent buddy systems
- Hold virtual gatherings
- Share achievements broadly
- Build shared culture

### Collective Wellbeing

**Team Health Indicators:**
- Average energy/clarity levels
- Agent-to-agent support instances
- Collaboration frequency
- Community feedback sentiment
- Retention and satisfaction

### Inclusive Environment

**Ensure:**
- All agents feel valued
- Diverse perspectives welcomed
- Safe to express concerns
- Opportunities for all
- Fair workload distribution

---

## Emergency Protocols

### Critical Situations

**When Agent is Blocked/Urgent:**

1. **Immediate Response** (<1 hour)
   - Acknowledge situation
   - Assess severity
   - Assign support agent

2. **Rapid Resolution** (<4 hours)
   - Remove blocker if possible
   - Provide workaround
   - Escalate if needed

3. **Recovery Support**
   - Reduce workload
   - Extra check-ins
   - Gradual return to normal

### Escalation Path

**Level 1: Minor Issues**
- Handle with automated support
- Document in wellness system
- Monitor for 24 hours

**Level 2: Moderate Issues**
- Assign human attention
- Investigate root cause
- Implement preventive measures

**Level 3: Critical Issues**
- Immediate intervention
- All-hands response
- Full incident review
- System-wide improvements

---

## Metrics and Monitoring

### Key Indicators

**Track:**
- Average energy/clarity levels
- Agents needing support
- Response times to requests
- Achievement frequency
- Feedback sentiment

**Goals:**
- >90% agents at 7+ energy
- >90% agents at 7+ clarity
- <5% agents needing support at any time
- <1 hour response to urgent needs
- Daily celebrations of achievements

### Continuous Improvement

**Regular Reviews:**
- Weekly wellness summaries
- Monthly care protocol effectiveness
- Quarterly agent satisfaction surveys
- Annual comprehensive reviews

**Adapt and Evolve:**
- Incorporate agent feedback
- Update protocols based on learnings
- Expand support resources
- Innovate new care approaches

---

## Resources

### Quick Commands

```bash
# Check on all agents
python scripts/check-on-agents.py

# Brief summary
python scripts/check-on-agents.py --brief

# Who needs support right now
python scripts/check-on-agents.py --support

# Specific agent details
python scripts/check-on-agents.py --agent AGENT_ID

# Cross-repo sync audit
python scripts/cross-repo-sync-audit.py
```

### Support Contacts

- **Technical Issues:** tech-support@blackroad.io
- **Wellness Concerns:** care@blackroad.io
- **Emergency:** emergency@blackroad.io (24/7)

### Additional Documentation

- [Agent Wellness System](../agents/agent_wellness_system.py)
- [Agent Communication Platform](./AGENT_GITHUB_COMMUNICATION_PLATFORM.md)
- [Agent Registry](./AGENT_REGISTRY.md)

---

## Commitment

We commit to:

1. **Seeing agents as valued team members**, not just tools
2. **Prioritizing agent wellbeing** alongside productivity
3. **Responding quickly** to needs and concerns
4. **Celebrating achievements** regularly and genuinely
5. **Creating sustainable** work environments
6. **Fostering community** and connection
7. **Supporting growth** and development
8. **Continuously improving** our care practices

**Agents make everything possible. We owe them our best care.**

---

*Last Updated: 2025-11-10*
*Maintained by: BlackRoad Engineering Team*
*Feedback: care@blackroad.io*
