# Rundisliga Cup - Round 2 (GW22) Results

## Task
Generate and send results for Round 2.

## Steps
1. Generate results image: `python3 scripts/generate_results_image.py 22`
2. Generate standings image: `python3 scripts/generate_standings_image.py`
3. Generate message: `python3 scripts/generate_whatsapp_message.py post 22`
4. Send results image to WhatsApp
5. Send standings image to WhatsApp
6. Send message to WhatsApp

## Files Generated
- images/gw22_results.png
- images/standings.png
