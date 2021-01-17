# m1finance-piediff
[M1 Finance's](https://www.m1finance.com/) an unofficial tool to compare 2 pies (yours and shared one)

Sometimes you need to compare two pies to see a slice difference between them. For example, it is super useful to use this tool to keep up to date your pie from a shared pie. So you can compare your pie and shared pie and see the difference. 

![sampleone](https://github.com/rooty0/m1finance-piediff/blob/main/example.jpeg?raw=true)

 
Unfortunately, [M1 Finance](https://www.m1finance.com/) does not provide any API to make this task easy so as a result you can see selenium as a dependency.
Basically you need to download a single binary file to your system, see install section below


### Dependencies
- **selenium** https://www.selenium.dev/


### To Install
Selenium requires a driver to interface with your favorite browser.
Firefox, for example, requires geckodriver, which needs to be installed before the script can be run.
Check [Drivers](https://selenium-python.readthedocs.io/installation.html#drivers) section for more info how to install it

After you got the driver, follow the steps below
```shell script
git clone https://github.com/rooty0/m1finance-piediff.git
cd m1finance-piediff
cp config.example.yaml config.yaml
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### Configuration
You need to edit `config.yaml` configuration file

First open your browser and login to [M1 Finance](https://www.m1finance.com/).
Then open a session storage of your browser and copy `m1_finance_auth.refreshToken` (option `REFRESH_TOKEN`) to the configuration file.
An example how to access session storage for `Chrome`:

```
right click on a page --> Inspect --> Application --> Sessions Storage --> dashboard.m1finance.com 
```

Assuming you already downloaded a binary file selenium driver, you need to provide a full path to the file to option `SELENIUM_DRIVER_PATH`.

Provide full links to `SHARED_PIE` and `MY_PIE`

### To Run
```shell script
venv/bin/python piediff.py
```