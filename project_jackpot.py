#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project_jackpot - jero98772

import uvicorn

from core.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=9600,
    )
