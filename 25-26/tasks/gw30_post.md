# Rundisliga Cup - Round 9 (GW30) Results

## Task
Generate and send results for Round 9.

## Steps
1. Generate results image: `python3 scripts/generate_results_image.py 30`
2. Generate standings image: `python3 scripts/generate_standings_image.py`
3. Generate message: `python3 scripts/generate_whatsapp_message.py post 30`
4. Send results image to WhatsApp
5. Send standings image to WhatsApp
6. Send message to WhatsApp

## Files Generated
- images/gw30_results.png
- images/standings.png
