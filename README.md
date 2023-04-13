# Stock analysis bot
##### All using Python 3.9 version
You can run install_lib.sh file for install all library (version 2)
&nbsp;
##### Bot version 3 is coming, You can run the main_ver3.py file to trt it out before actually using it soon.
##### detail:
- more flexible
- easy to use
&nbsp;
##### how to config bot version 3?
- config indicator parameter have 2 choice
    - long_indicator file for long-term data analysis
    - short_indicator file for short-term data analysis
- config to using indicators in config/config.json.
    - mode parameter contain 2 modes:
        - stock
        - fund
        - crypto (soon)
    - fetch_newdata parameter is pull data at frist or not
    - len_data parameter is number of rows in data
- config select stock name in config/list_stock/stock_config.json
    - currenly support only fund and stock (as soon will support cryptocurrency)