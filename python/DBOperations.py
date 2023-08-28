# database_operations.py
import sqlite3
from datetime import datetime
from tkinter import messagebox



class DatabaseOperations:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None
    def create_connection(self):
        if self.connection:
            print("Connection is already open.")
            return
        try:
            self.connection = sqlite3.connect(self.db_file)
        except sqlite3.Error as e:
            print(f"Error occurred while creating the connection: {e}")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_table_if_not_exists(self, table_name, columns):
        if not self.connection:
            raise ValueError("SQLite connection not established. Call create_connection() first.")
        try:
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.connection.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")
        
    def insert_data_into_table(self, table_name, column_names, data=None, data_values=None):
        if not self.connection:
            self.create_connection()
        if data is None and data_values is None:
            raise ValueError("Either 'data' or 'data_values' must be provided.")
        if data is not None and data_values is not None:
            raise ValueError("Only one of 'data' or 'data_values' should be provided.")
        try:
            if data is not None:
                data_with_dates_converted = []
                for value in data:
                    if isinstance(value, datetime):
                        date_str = value.strftime("%d-%m-%Y")
                        data_with_dates_converted.append(date_str)
                    else:
                        data_with_dates_converted.append(value)
            else:
                data_with_dates_converted = data_values

            placeholders = ",".join([f":{col}" for col in column_names])
            query = f"INSERT OR REPLACE INTO {table_name} ({','.join(column_names)}) VALUES ({placeholders})"
            named_data = dict(zip(column_names, data_with_dates_converted))
            cursor = self.connection.execute(query, named_data)
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error occurred while inserting data: {e}")
            
    def get_maps(self):
        if not self.connection:
            self.create_connection()
        try:
            query = f"SELECT distinct map.map_id, map.map_name FROM tbt_maps map, tbt_sources src,tbt_destinations dst WHERE map.map_id = src.map_id and map.map_id = dst.map_id order by map.map_id asc"
            cursor = self.connection.execute(query)
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Error occurred while fetching data: {e}")
            return None
            
    def get_map_data(self, mapName):
        if not self.connection:
            self.create_connection()
        try:
            query = f"SELECT * FROM tbt_maps WHERE map_name = ?"
            cursor = self.connection.execute(query, (mapName,))
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Error occurred while fetching data: {e}")
            return None
        
    def get_dest_data(self,mapName):
        if not self.connection:
            self.create_connection()
        try:
            query = f"SELECT dest_name, position,color,direction FROM tbt_destinations as td Join tbt_maps tm On tm.map_id = td.map_id where tm.map_name = ?"
            cursor = self.connection.execute(query, (mapName,))
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Error occurred while fetching data: {e}")
            return None
    
    def get_source_data(self,mapName):
        if not self.connection:
            self.create_connection()
        try:
            query = f"SELECT position,direction FROM tbt_sources as ts Join tbt_maps tm On tm.map_id = ts.map_id where tm.map_name = ?"
            cursor = self.connection.execute(query, (mapName,))
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Error occurred while fetching data: {e}")
            return None
            
    def isDuplicateMapName(self, mapName=None):
        if not self.connection:
            self.create_connection()
        try:
            query = f"SELECT * FROM tbt_maps WHERE map_name = ?"
            cursor = self.connection.execute(query, (mapName,))
            results = cursor.fetchall()
            return len(results) > 0
        except sqlite3.Error as e:
            print(f"Error occurred while fetching data: {e}")
            return None

    def isDuplicateDestName(self, destName=None, mapid=None):
        if not self.connection:
            self.create_connection()
        try:
            query = f"SELECT * FROM tbt_destinations WHERE dest_name = ? AND map_id = ?"
            cursor = self.connection.execute(query, (destName,mapid,))
            results = cursor.fetchall()
            return len(results) > 0
        except sqlite3.Error as e:
            print(f"Error occurred while fetching data: {e}")
            return None
            
    def update_data(self, table_name, column_name, new_value, condition=None, condition_params=None):
        if not self.connection:
            self.create_connection()
        try:
            query = f"UPDATE {table_name} SET {column_name} = ?"
            if condition:
                query += f" WHERE {condition}"
            params = (new_value,) if condition_params is None else (new_value,) + condition_params
            self.connection.execute(query, params)
            self.connection.commit()
            messagebox.showinfo('Update', column_name+" updated successfully.")
        except sqlite3.Error as e:
            print(f"Error occurred while updating data: {e}")
            
            
    def get_config(self,config_name):
        if not self.connection:
            self.create_connection()
        try:
            query = f"SELECT config_name, config_value FROM tbt_mst_config WHERE config_name = ?"
            
            cursor = self.connection.execute(query, (config_name,))
            results = cursor.fetchall()
            if(len(results) == 0 and config_name=="Ip Address"):
                messagebox.showinfo('Error','Please Enter the IP address to Connect!')
            elif(len(results) == 0 and config_name=="Thread Duration"):
                messagebox.showinfo('Error','Please Enter the Thread Durations to Start!')
            return results
            
        except sqlite3.Error as e:
            print(f"Error occurred while updating data: {e}")
            
            
    def get_path_data(self, destName=None,mapName=None):
        if not self.connection:
            self.create_connection()
        try:
            query = f"SELECT path_value FROM tbt_paths path, tbt_maps map WHERE map.map_name = ? AND map.map_id = path.map_id AND path.dest_name = ?"
            cursor = self.connection.execute(query, (mapName,destName))
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Error occurred while fetching data: {e}")
            return None