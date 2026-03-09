# Alert Escalation Policy

**Version**: 1.0
**Last Updated**: 2026-03-08
**Owner**: SRE Team

## Severity Levels

| Severity | Name | Response Time | Impact | Example |
|----------|------|---------------|--------|---------|
| P0 | Critical | < 5 min | Complete outage | Colony down, data corruption |
| P1 | High | < 15 min | Major degradation | Dependency failure, high latency |
| P2 | Medium | < 30 min | Minor degradation | Single feature broken |
| P3 | Low | < 1 hour | Noticeable issue | Performance below baseline |

## Escalation Paths

### P0 - Critical Incidents

```
Level 1 (0-5 min):
  @on-call-engineer
    ↓ (5 min, no response)
  @on-call-manager
    ↓ (10 min, no response)
  @engineering-director
    ↓ (15 min, no response)
  @cto
    ↓ (30 min, no response)
  @ceo + @board
```

### P1 - High Severity

```
Level 1 (0-15 min):
  @on-call-engineer
    ↓ (15 min, no response)
  @on-call-manager
    ↓ (30 min, no response)
  @engineering-director
    ↓ (45 min, no response)
  @cto
```

### P2 - Medium Severity

```
Level 1 (0-30 min):
  @on-call-engineer
    ↓ (30 min, no response)
  @on-call-manager
    ↓ (60 min, no response)
  @engineering-director
```

### P3 - Low Severity

```
Level 1 (0-60 min):
  @on-call-engineer
    ↓ (1 hour, no response)
  @on-call-manager
    ↓ (2 hours, no response)
  @team-lead
```

## On-Call Rotation

### Primary On-Call
- **Role**: Primary Responder
- **Coverage**: 24/7
- **Rotation**: Weekly
- **Handoff**: Monday 9:00 AM UTC

### Secondary On-Call
- **Role**: Backup / Shadow
- **Coverage**: Business hours (9 AM - 9 PM UTC)
- **Rotation**: Weekly
- **Purpose**: Learning, backup support

### On-Call Responsibilities

**Primary**:
- Respond to all alerts within SLA
- Acknowledge alerts within 5 min
- Begin investigation within 10 min
- Document all actions
- Escalate if needed

**Secondary**:
- Shadow primary during business hours
- Assist with complex incidents
- Cover for primary during breaks
- Learn from incidents

## Notification Channels

### P0 - Critical
1. **Phone call** (immediate)
2. **SMS** (immediate)
3. **Slack** (@here, #incidents)
4. **Email** (incident mailing list)
5. **PagerDuty** (high urgency)

### P1 - High
1. **SMS** (immediate)
2. **Slack** (@on-call, #incidents)
3. **Email** (incident mailing list)
4. **PagerDuty** (high urgency)

### P2 - Medium
1. **Slack** (@on-call)
2. **Email** (incident mailing list)
3. **PagerDuty** (low urgency)

### P3 - Low
1. **Slack** (@on-call)
2. **Email** (daily digest)
3. **PagerDuty** (info only)

## Incident Roles

### Incident Commander (IC)
- Leads incident response
- Makes final decisions
- Coordinates communication
- Declares incident resolved

### Communications Lead
- Manages external communication
- Updates status page
- Drafts customer notifications
- Handles press inquiries (if needed)

### SRE Lead
- Technical investigation
- Implements fixes
- Documents technical details
- Leads postmortem

### Security Lead (if needed)
- Assesses security impact
- Coordinates security response
- Implements security controls
- Documents security findings

### Engineering Support
- Provides domain expertise
- Assists with implementation
- Reviews proposed fixes
- Tests solutions

## War Room Procedures

### Activation
1. IC declares incident in #incidents
2. Create dedicated incident channel (#incident-XXX)
3. Add all relevant roles
4. Start incident tracking document

### Incident Channel Template
```
# Incident #XXX - [Brief Description]

**Severity**: P0/P1/P2/P3
**Status**: Investigating / Identified / Monitoring / Resolved
**IC**: @username
**Started**: [Timestamp]
**Last Update**: [Timestamp]

## Timeline
- [Timestamp] - Incident detected
- [Timestamp] - Status update

## Actions Taken
- [Action item]
- [Action item]

## Next Steps
- [ ] [Action]
- [ ] [Action]

## Artifacts
- Runbook: [link]
- Logs: [link]
- Dashboard: [link]
```

### Communication Update Frequency
| Severity | Update Frequency |
|----------|------------------|
| P0 | Every 15 minutes |
| P1 | Every 30 minutes |
| P2 | Every hour |
| P3 | Every 4 hours |

## Escalation Triggers

### Automatic Escalation
- No acknowledgment within 50% of SLA
- No progress update within 100% of SLA
- Incident severity increases
- Multiple customers affected

### Manual Escalation
- IC needs additional resources
- IC is unavailable
- Complexity exceeds IC's expertise
- Executive visibility needed

## Post-Incident Procedures

### Immediate (0-24 hours)
1. **Incident Document**
   - Complete timeline
   - All actions taken
   - Root cause analysis
   - Resolution steps

2. **Communication**
   - Customer postmortem (if needed)
   - Internal summary
   - Status page update

3. **Monitoring**
   - Enhanced monitoring for 24h
   - Watch for recurrence
   - Validate fix effectiveness

### Short-term (1-7 days)
1. **Postmortem Meeting**
   - Schedule within 5 days
   - All participants attend
   - Document action items

2. **Action Items**
   - Create tickets for improvements
   - Assign owners
   - Set due dates

3. **Runbook Updates**
   - Update based on lessons learned
   - Add new scenarios
   - Improve procedures

### Long-term (1-3 months)
1. **Process Improvements**
   - Review escalation effectiveness
   - Update SLAs if needed
   - Improve monitoring/alerting

2. **Training**
   - Train team on lessons learned
   - Update on-call training
   - Improve documentation

3. **Architecture Review**
   - Review underlying issues
   - Plan improvements
   - Implement fixes

## On-Call Compensation

### Per-Diems
- **Primary on-call**: $X/day
- **Secondary on-call**: $Y/day
- **Holiday/Weekend**: 2x multiplier

### Incident Pay
- **P0 incidents**: $Y/incident
- **P1 incidents**: $Y/incident
- **After-hours incidents**: 1.5x multiplier

### Time Off in Lieu (TOIL)
- **For incidents > 2 hours**: Equal TOIL
- **For postmortems**: Add to TOIL bank
- **Maximum TOIL accrual**: 40 hours

## On-Call Health

### Best Practices
- **Maximum rotation**: 2 weeks consecutive
- **Minimum break**: 1 week between rotations
- **No on-call during vacation**
- **Swap coverage if sick**

### Burnout Prevention
- Monitor on-call load
- Regular rotation reviews
- Anonymous feedback channel
- Mental health resources

### Training Requirements
- **New engineers**: Shadow 2 rotations
- **Quarterly training**: Incident response drills
- **Annual review**: Escalation policy updates
- **Runbook reviews**: Monthly

## Contact Information

### Emergency Contacts
- **On-Call Phone**: +1-XXX-XXX-XXXX
- **Emergency Line**: +1-XXX-XXX-XXXX (executive only)
- **Security**: security@example.com

### Non-Emergency
- **SRE Team**: sre@example.com
- **Engineering**: eng@example.com
- **Support**: support@example.com

## Related Documents
- [Runbooks](../runbooks/)
- [SLOs](../slos/)
- [Disaster Recovery](./disaster-recovery.md)
- [Security Incident Response](./security-incident-response.md)

---

**Approval**:
- **SRE Lead**: ______________________
- **Engineering Director**: ______________________
- **CTO**: ______________________

**Last Reviewed**: 2026-03-08
**Next Review**: 2026-06-08
