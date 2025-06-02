import os
import win32com.client as win32
import logging

def convert_xls_to_xlsx(folder):
    """
    Converts all .xls files in the given folder to .xlsx format using Excel COM automation.
    Deletes the .xls file only after successful conversion. Logs all actions and errors.
    """
    log_file = os.path.join(folder, 'xls_to_xlsx_conversion.log')
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False
    for filename in os.listdir(folder):
        if filename.lower().endswith('.xls') and not filename.lower().endswith('.xlsx'):
            xls_path = os.path.join(folder, filename)
            xlsx_path = os.path.splitext(xls_path)[0] + '.xlsx'
            logging.info(f"Converting: {xls_path} -> {xlsx_path}")
            try:
                wb = excel.Workbooks.Open(xls_path)
                wb.SaveAs(xlsx_path, FileFormat=51)  # 51 is the code for .xlsx
                wb.Close(False)
                if os.path.exists(xlsx_path):
                    os.remove(xls_path)
                    logging.info(f"Success: {xlsx_path} (deleted original .xls)")
                else:
                    logging.error(f"Conversion failed: {xlsx_path} not found after save.")
            except Exception as e:
                logging.error(f"Failed to convert {xls_path}: {e}")
    excel.Quit()

if __name__ == "__main__":
    folder = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Data\_CF"
    convert_xls_to_xlsx(folder) 