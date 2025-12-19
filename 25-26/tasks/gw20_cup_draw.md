# Rundisliga Cup 25/26 - OFFICIAL DRAW

## Task
Generate the official Swiss draw and send the announcement to the WhatsApp group.

## Steps

### 1. Reset Cup Standings
The cup starts fresh - reset all points to 0:
```bash
# Points will be tracked separately from regular H2H league
```

### 2. Generate the Swiss Draw
```bash
python3 scripts/generate_swiss_draw.py
```

This creates 10 rounds of fixtures where each team plays 10 different opponents.

### 3. Generate the Draw Announcement Message
```bash
python3 scripts/generate_whatsapp_message.py draw
```

### 4. Generate Fixtures Image (Optional)
Consider creating a fixtures image to share.

### 5. Send to WhatsApp Group
Copy and send:
- The draw announcement message
- Optionally the full fixture list or fixtures image

## Message Template

```
🚨 RUNDISLIGA CUP 25/26 DRAW COMPLETE 🚨

THE SWISS DRAW HAS BEEN MADE

EACH TEAM WILL PLAY 10 OPPONENTS OVER 10 ROUNDS
WIN = 3 POINTS | DRAW = 1 POINT | LOSS = 0 POINTS

TOP 8 AFTER 10 ROUNDS QUALIFY FOR THE KNOCKOUT STAGES

🚨 ROUND 1 FIXTURES (GW21 - TUE JAN 6) 🚨

[FIXTURE LIST]

FULL FIXTURE LIST: [LINK TO GITHUB OR IMAGE]

GOOD LUCK TO ALL MANAGERS 🍀
```

## Important
- This is the OFFICIAL draw - once sent, fixtures are locked
- Cup starts in 2 days (GW21 - Tue Jan 6, 2026)
