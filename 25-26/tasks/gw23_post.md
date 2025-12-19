# Rundisliga Cup - Round 3 (GW23) Results

## Task
Generate and send results for Round 3.

## Steps
1. Generate results image: `python3 scripts/generate_results_image.py 23`
2. Generate standings image: `python3 scripts/generate_standings_image.py`
3. Generate message: `python3 scripts/generate_whatsapp_message.py post 23`
4. Send results image to WhatsApp
5. Send standings image to WhatsApp
6. Send message to WhatsApp

## Files Generated
- images/gw23_results.png
- images/standings.png
