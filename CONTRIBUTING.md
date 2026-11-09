# Contributing

Bug reports, ideas, and pull requests are welcome. Please use the issue templates and include your Windows version, steps to reproduce, and relevant logs. Never include personal audio device identifiers or other private data.

## Development

Use Windows 10/11 with Python 3.12, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python audio_router_gui.py
```

Keep changes focused, avoid new dependencies without a clear need, and describe manual Windows checks in your pull request. I aim to acknowledge new issues within one day; troubleshooting may take longer.
