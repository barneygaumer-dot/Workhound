#!/usr/bin/env python3
import argparse
from workhound import create_app
from workhound.version import __version__

def main():
    p = argparse.ArgumentParser(description="WolfPack WorkHound")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--debug", action="store_true")
    p.add_argument("--version", action="store_true")
    args = p.parse_args()
    if args.version:
        print(__version__)
        return
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
