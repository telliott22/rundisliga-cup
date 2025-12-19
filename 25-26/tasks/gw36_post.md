# Rundisliga Cup - SF1 (GW36) Results

## Task
Generate and send results for SF1.

## Steps
1. Generate results image: `python3 scripts/generate_results_image.py 36`
2. Generate message: `python3 scripts/generate_whatsapp_message.py post 36`
3. Send results image to WhatsApp
4. Send message to WhatsApp
5. If 2nd leg - include aggregate scores and who advances

## Files Generated
- images/gw36_results.png
