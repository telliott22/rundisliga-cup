# Rundisliga Cup - QF2 (GW34) Results

## Task
Generate and send results for QF2.

## Steps
1. Generate results image: `python3 scripts/generate_results_image.py 34`
2. Generate message: `python3 scripts/generate_whatsapp_message.py post 34`
3. Send results image to WhatsApp
4. Send message to WhatsApp
5. If 2nd leg - include aggregate scores and who advances

## Files Generated
- images/gw34_results.png
