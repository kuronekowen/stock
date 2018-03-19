# -*- coding: utf-8 -*-
import pyodbc
import re
import csv
from datetime import datetime
import glob
import time

class dbHandle:

    def __init__( self, server, database, username, password ):

        cmd = """SET LANGUAGE us_english; set dateformat ymd;"""
        print( "Initial Database connection..." + database )
        self.con_db = pyodbc.connect( 'DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + server +
                                      ';PORT=1443;DATABASE=' + database +
                                      ';UID=' + username +
                                      ';PWD=' + password )

        self.cur_db = self.con_db.cursor( )
        self.date = ''
        self.stock = None
        self.con_db.commit( )
        self.cur_db.execute( cmd )

    def ResetTable( self, table ):

        cmd = 'DROP TABLE IF EXISTS ' + table

        # Do some setup
        with self.cur_db.execute( cmd ):
            print( 'Successfully Del' + table )

    def CreateTable( self ):

        """確認一定長度，且只會有英數字：char
                        確認一定長度，且可能會用非英數以外的字元：nchar
                        長度可變動，且只會有英數字：varchar
                        長度可變動，且可能會用非英數以外的字元：nvarchar
                        price decimal( 8, 2 ) NOT NULL
                        最大位數8位數包含小數點前6位，小數點後2位，或小數點前8位，小數點無"""

        cmd = ''' CREATE TABLE dbo.BROKERAGE
	(
	stock varchar(10) COLLATE　Chinese_Taiwan_Stroke_CS_AS NOT NULL,
	date date NOT NULL,
	brokerage char(4) COLLATE　Chinese_Taiwan_Stroke_CS_AS NOT NULL,
	brokerage_name varchar(10) COLLATE　Chinese_Taiwan_Stroke_CS_AS NOT NULL,
	price decimal( 8, 2 ) NOT NULL,
	buy_volume decimal( 16, 0 ) NULL,
	sell_volume decimal( 16, 0 ) NULL
	)  ON [PRIMARY]

    COMMIT'''

        with self.cur_db.execute( cmd ):
            print( 'Successfully Create BROKERAGE' )


    def InsertCSV2DB( self, filename ):

        f = open( filename, 'r', encoding = 'utf8', errors = 'ignore' )

        for row in csv.reader( f ):
            if row[ 0 ] == '':
                return

            brokerage_symbol = row[ 1 ][ 0:4 ]
            brokerage_name = row[ 1 ][ 4:len( row[ 1 ] ) ].replace( ' ', '' ).replace( '\u3000', '' )
            price       = row[ 2 ]
            buy_volume  = row[ 3 ]
            sell_volume = row[ 4 ]

            cmd = 'INSERT INTO BROKERAGE ( stock, date, brokerage, brokerage_name, price, buy_volume, sell_volume ) \
                   VALUES ( ?, ?, ?, ?, ?, ?, ? )'
            try:
                row = ( self.stock, self.date, brokerage_symbol, brokerage_name, price, buy_volume, sell_volume )
                self.cur_db.execute( cmd, row )
            except:
                print( '寫入失敗', row )


    def InsertDB( self ):

        for filename in glob.glob( './/**//*.csv' ):

            self.date = filename[ -10:-4 ]

            self.stock = re.sub( '[0-9]+\\\\', '', filename.split( '_' )[ 1 ] )

            stock_name = filename.split( '_' )[ 2 ]
            # ----------------------------------------

            print( self.stock, stock_name, self.date )

            cmd = 'SELECT stock, date FROM BROKERAGE WHERE stock = \'{}\' and date = \'{}\''.format( self.stock, self.date )

            ft = self.cur_db.execute( cmd ).fetchone( )

            if ft is None:
                self.InsertCSV2DB( filename )
                self.con_db.commit( )
            else:
                print( '資料已存在資料庫 ', filename )

def main( ):

    try:
        db = dbHandle( 'localhost', 'StockDB', 'sa', "admin" )
    except Exception as e:
        db = dbHandle( 'localhost', 'StockDB', 'sa', "292929" )
        print( '{}'.format( e ) )

    db.ResetTable( 'BROKERAGE' )
    db.CreateTable(  )
    db.InsertDB( )

if __name__ == '__main__':

    start_tmr = time.time( )
    main( )
    print( 'The script took {:06.1f} minute !'.format( (time.time( ) - start_tmr) / 60 ) )