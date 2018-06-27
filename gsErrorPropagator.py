#!/usr/local/bin/python3
# pip3 install --upgrade google-api-python-client
from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# try:
# 	import argparse
# 	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
# 	flags = None

from uncertainties import ufloat
from uncertainties.umath import *
from math import pi,e 
from string import digits
from string import ascii_uppercase

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/<FILE>.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'CalcUncert'
# SPREADSHEET_ID = '14mTO5A3tgtcD1HkgItetVGgwcczSAtGUIPGuaK7GdBY'

def get_credentials():
	"""Gets valid user credentials from storage.

	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
		Credentials, the obtained credential.
	"""
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,
								   'sheets.googleapis.calc-uncert.json')

	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		# if flags:
		# 	credentials = tools.run_flow(flow, store, flags)
		# else: # Needed only for compatibility with Python 2.6
		# 	credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials

def getUNCCells(valueRanges):
	output=[]
	for valueRange in valueRanges:
		rangeStr=valueRange['range']
		rows=valueRange['values']
		r=0
		for row in rows:
			c=0
			for cell in row:
				if type(cell) == str and cell[:5] == '=UNC(':
					output.append(UNCCell(r,c,rangeStr,cell))
				c+=1
			r+=1
	return output

class UNCCell:
	def __init__(self,row,column,parentRange,formula):
		self.row = row
		self.column = column
		self.sheet = parentRange.split('!')[0]
		self.formula = formula
		self.A1Notation = self.mkA1Notation()
		self.originalFormulaArgs = formula[5:-1].split(',')
		self.formulaArgs = self.formula[5:-1].split(',')
		self.usedRanges = []
		self.formulaArgTypes = self.mkArgTypes()
	def __str__(self):
		return '\tA1Notation: '+self.A1Notation+'\n'+\
				'\tRow: '+str(self.row)+\
				'\tCol: '+str(self.column)+\
				'\n\tFormula: '+self.formula+\
				'\n\tOriginal Formula Args: '+str(self.originalFormulaArgs)+\
				'\n\tFormula Args: '+str(self.formulaArgs)+\
				'\n\tArg Types: '+str(self.formulaArgTypes)+\
				'\n\tUsed Ranges: '+str(self.usedRanges)
	def mkA1Notation(self):
		return self.sheet+'!'+colToAlpha(self.column + 1) + str(self.row + 1)
	def mkArgTypes(self):
		out = []
		i=1
		for arg in self.formulaArgs[1:]:
			isFloat=True
			try:
				float(arg)
			except Exception as e:
				isFloat=False
			if isFloat:
				out.append('num')
			elif arg[0] == '"' and arg[-1] == '"':
				out.append('str')
				self.formulaArgs[i] = arg.split('"')[1]
			else:
				if len(arg.split('!')) == 1:
					self.formulaArgs[i] = self.sheet+'!'+self.formulaArgs[i].replace('$','')
				self.usedRanges.append(self.formulaArgs[i].replace('$',''))
				out.append('range')
			i+=1
		return out
	def mkFormula(self):
		return '=UNC('+','.join(self.originalFormulaArgs)+')'
	def __eq__(self, other):
		# print('Eq')
		return other.A1Notation not in self.usedRanges and self.A1Notation not in other.usedRanges
	def __gt__(self, other):
		# print(self.A1Notation,'is gt than',other.A1Notation,'? ',other.A1Notation in self.usedRanges)
		return other.A1Notation in self.usedRanges
	
def calcUfloat(formulaCalc, ufloats, errType):
	#loop defining all vars
	for i in range(0, len(ufloats), 3):
		exec(ufloats[i] + "=" + "ufloat(float("+ str(ufloats[i+1]) + "), float("+ str(ufloats[i+2]) + "))")
	result = eval(formulaCalc)
	return eval('result'+'.'+errType)

class cell():
	def __init__(self, A1Notation, indexOffset=0):
		if not isinstance(indexOffset, int):
			indexOffset=0
		aux = A1Notation.split('!')
		self.sheet = aux[0]
		aux[1] = ''.join(aux[1].split('$'))
		i=1
		for char in aux[1][1:]:
			if char in digits[1:]:
				break
			i+=1
		self.row=indexOffset
		self.row+= int(aux[1][i:]) - 1
		chars = aux[1][:i][::-1]
		self.column=indexOffset
		i=0
		for char in chars:
			self.column+=26**i*(ascii_uppercase.index(char) + 1)
			i+=1
		self.column-=1

def getValue(A1Notation, valueRanges):
	inputCell = cell(A1Notation)
	for valueRange in valueRanges:
		if valueRange['sheet'] == inputCell.sheet:
			return valueRange['values'][inputCell.row][inputCell.column]
def setValue(value , A1Notation, valueRanges):
	inputCell = cell(A1Notation)
	for valueRange in valueRanges:
		if valueRange['sheet'] == inputCell.sheet:
			valueRange['values'][inputCell.row][inputCell.column] = value

def colToAlpha(column):
	c = []
	while column > 26:
		c.append(chr((column-1)%26+65))
		if column % 26 == 0:
			column = (column-1) // 26
		else:
			column = (column) // 26
	c.append(chr(column+64))
	c.reverse()
	return ''.join(c)

def main():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
					'version=v4')
	service = discovery.build('sheets', 'v4', http=http,
							  discoveryServiceUrl=discoveryUrl)
	if len(sys.argv) != 2 :
		print ("Please run the program followed by the spreadsheet ID")
		return
	else:
		spreadsheetId = sys.argv[1]
	sheets = service.spreadsheets().get(
		spreadsheetId=spreadsheetId).execute()['sheets']
	rangeNames = []
	for sheet in sheets:
		# rangeNames.append(sheet['properties']['title'])
		rangeNames.append(sheet['properties']['title']+'!'+'A1:'+\
			colToAlpha(sheet['properties']['gridProperties']['columnCount'])+\
			str(sheet['properties']['gridProperties']['rowCount']))
	formulaValueRanges = service.spreadsheets().values().batchGet(
		spreadsheetId=spreadsheetId, ranges=rangeNames,valueRenderOption='FORMULA').execute()['valueRanges']
	valueRanges = service.spreadsheets().values().batchGet(
		spreadsheetId=spreadsheetId, ranges=rangeNames,valueRenderOption='UNFORMATTED_VALUE').execute()['valueRanges']
	# Add sheet info to value Cells
	for valueRange in valueRanges:
		valueRange['sheet'] = valueRange['range'].split('!')[0]
	# for x in getUNCCells(formulaValueRanges):
		# print(x.A1Notation)
	UNCCells = sorted(getUNCCells(formulaValueRanges))
	# print('After:')
	# for x in UNCCells:
	# 	print(x.A1Notation)

	data = []

	for UNCCell in UNCCells:
		try:
			i=1
			argValues = []
			for arg in UNCCell.formulaArgTypes:
				if arg == 'range':
					argValues.append(getValue(UNCCell.formulaArgs[i],valueRanges))
				else:
					argValues.append(UNCCell.formulaArgs[i])
				i+=1
			newValue = calcUfloat(argValues[0],argValues[1:-1],argValues[-1])
			UNCCell.originalFormulaArgs[0] = str(newValue)
			# Update corresponding cell value
			setValue(newValue, UNCCell.A1Notation, valueRanges)
			data.append({'range':UNCCell.A1Notation, 'majorDimension':'ROWS','values':[[UNCCell.mkFormula()]]})
		except Exception as e:
			print('Error while processing:')
			print(UNCCell)
			# raise e

	body = { "valueInputOption": "USER_ENTERED",
			"data": data}
	service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId,body=body).execute()

if __name__ == '__main__':
	main()