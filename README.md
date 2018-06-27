# gsErrorPropagator
This is an uncertainty calculator add-on for Google Spreadsheets which allows the user to retrieve the number value, standard deviation and maximum error associated with measurements that follow a known model. Unleash the power of uncertainties in Google Spreadsheets.

## Instalation
1. First, you will need to install python3 and pip3 in your OS according to the Python documentation that you can find in the official website.
2. Now you must install some packages. Let's start with the "oauth2client" one. Just open your terminal, type and run the following line:
```
pip3 install oauth2client
```
3. After that, type and run:
```
pip3 install --upgrade google-api-python-client
```
4. Now you need to pull the project files from git. Change the directory in the command line to where you want the files to be located, then type and run:
```
git clone https://github.com/caenrigen/gsErrorPropagator.git
```
5. IF you have macOS or Linux, you can run this line that allows you to run gsErrorPropagator.py from any path in which your terminal is stationed. Be careful to write the original path in the designated place ("clonepath").
```
echo 'export PATH="clonepath":${PATH}' >> $HOME/.bash_profile
```
6. At last, just connect the Add-On with your Google account. For that, just follow this link:
```
https://chrome.google.com/webstore/detail/unc/bppaocmhleknjbchhmpbfoeifgbplpcn?utm_source=permalink
```
## Usage Instructions
