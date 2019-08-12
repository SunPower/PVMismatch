import pandas as pd
import numpy as np
from pvmismatch.pvmismatch_lib import pvcell, pvconstants, pvmodule, pvstring, pvsystem

def _create_cell_pos_df(pv_mod, nrows, nr_string, nr_mod):
    """Create cell position dataframe of a module in the PV system"""
    cell_pos = pv_mod.cell_pos
    cell_pos_df = pd.DataFrame(index=['{}_{}'.format(nr_mod, nr) for nr in range(nrows)])
    b = 0
    for bypass in cell_pos:
        c = 0
        for col in bypass:
            cell_pos_df['{}_{}_{}'.format(nr_string, b, c)] = [i['idx'] for i in col]
            c = c+1
        b = b+1
    return cell_pos_df

def _create_irrad_df(pv_mod, cell_pos_df):
    """Create irradiance dataframe of a module in the PV system"""
    irrad = pd.Series(pv_mod.Ee.flatten())
    irrad_df = pd.DataFrame(index=cell_pos_df.index, columns=cell_pos_df.columns)
    for column in cell_pos_df.columns:
        for row in cell_pos_df.index:
            cell_index = cell_pos_df.loc[row, column]
            irrad_df.loc[row, column] = irrad[cell_index]
    return irrad_df

def _create_temp_df(pv_mod, cell_pos_df):
    """Create temperature dataframe of a module in the PV system"""
    temp = pd.Series(pv_mod.Tcell.flatten())
    temp_df = pd.DataFrame(index=cell_pos_df.index, columns=cell_pos_df.columns)
    for column in cell_pos_df.columns:
        for row in cell_pos_df.index:
            cell_index = cell_pos_df.loc[row, column]
            temp_df.loc[row, column] = temp[cell_index]
    return temp_df

def pvmm_system_layout_to_xls(xls_name, pv_sys, nrows):
    """Write an xls with worksheets of irradiance, cell temperature and cell index"""
    writer = pd.ExcelWriter(xls_name, engine='xlsxwriter')
    workbook = writer.book
    writer.sheets['CellIndexes'] = workbook.add_worksheet('CellIndexes')
    writer.sheets['Irradiance'] = workbook.add_worksheet('Irradiance')
    writer.sheets['CellTemp'] = workbook.add_worksheet('CellTemp')
    s = 0
    for string in pv_sys.pvstrs:
        m = 0
        for module in string.pvmods:
            cell_pos_df = _create_cell_pos_df(pv_mod=module, nrows=nrows, nr_string=s, nr_mod=m)
            if s == 0:
                startcol = 0
            else:
                ncols = int(module.numberCells / nrows)
                startcol = s*(ncols+1)
            if m == 0:
                startrow = 0
            else:
                startrow = m*(nrows+1)
            cell_pos_df.to_excel(writer, sheet_name='CellIndexes', startrow=startrow , startcol=startcol) # write cell pos
            irrad_df = _create_irrad_df(pv_mod=module, cell_pos_df=cell_pos_df)
            irrad_df.to_excel(writer, sheet_name='Irradiance', startrow=startrow , startcol=startcol) # write irrad
            temp_df = _create_temp_df(pv_mod=module, cell_pos_df=cell_pos_df)
            temp_df.to_excel(writer, sheet_name='CellTemp', startrow=startrow , startcol=startcol) # write irrad
            m = m + 1
        s = s + 1
    # formatting the irradiance worksheet
    writer.sheets['Irradiance'].conditional_format(0, 0, writer.sheets['Irradiance'].dim_rowmax, writer.sheets['Irradiance'].dim_colmax, {'type': '2_color_scale',
                                                                                                                                          'min_value':0,
                                                                                                                                          'max_value':1,
                                                                                                                                          'min_color':'#808080',
                                                                                                                                          'max_color':'#FFD700'})
    writer.save()
    writer.close()

def pvmm_set_suns_from_xls(input_xls_name, pv_sys, str_num, str_len, nrows):
    """Set suns of a PVMM PV system from an xls"""
    for string in list(range(str_num)):
        for module in list(range(str_len)):
            ncols = int(pv_sys.pvstrs[string].pvmods[module].numberCells / nrows)
            irrad = pd.read_excel(input_xls_name, sheet_name='Irradiance', skiprows=module*(nrows+1), nrows=nrows, usecols=range(string*(ncols+1), (string+1)*(ncols+1)), index_col=0, header=0)
            cell_pos = pd.read_excel(input_xls_name, sheet_name='CellIndexes', skiprows=module*(nrows+1), nrows=nrows, usecols=range(string*(ncols+1), (string+1)*(ncols+1)), index_col=0, header=0)
            Ee = []
            mod_cell_idxs = []
            for column in cell_pos.columns:
                for row in cell_pos.index:
                    Ee.append(irrad.loc[row, column])
                    mod_cell_idxs.append(cell_pos.loc[row, column])
            pv_sys.setSuns({string:{module:[Ee, mod_cell_idxs]}})
