import numpy as np
from scipy.interpolate import interp1d
# Pandas is an optional dependency only used by xlsio, therefore
# not installed with PVMismatch:
try:
    import pandas as pd
except ImportError:
    print("Pandas module not found. You need to install it before proceeding:")
    print("https://pandas.pydata.org/pandas-docs/stable/install.html")
    raise

def _create_cell_pos_df(pv_mod, nr_string, nr_mod):
    """Create cell position dataframe of a module in the PV system"""
    cell_pos = pv_mod.cell_pos
    nrows = int(pv_mod.numberCells / sum(pv_mod.subStrCells))
    cell_pos_df = pd.DataFrame(index=['{}_{}'.format(nr_mod, nr)
                                      for nr
                                      in range(nrows)])
    for b, bypass in enumerate(cell_pos):
        for c, col in enumerate(bypass):
            cell_pos_df['{}_{}_{}'.format(nr_string, b, c)] = [i['idx']
                                                               for i
                                                               in col]
    return cell_pos_df

def _create_nan_df(pv_mod, nr_string, nr_mod):
    """Create an "nan" dataframe of a module in the PV system for the case
    when the bypass diode activation is not calculated yet"""
    cell_pos = pv_mod.cell_pos
    nrows = int(pv_mod.numberCells / sum(pv_mod.subStrCells))
    nan_df = pd.DataFrame(index=['{}_{}'.format(nr_mod, nr)
                                 for nr
                                 in range(nrows)])
    for b, bypass in enumerate(cell_pos):
        for c, col in enumerate(bypass):
            nan_df['{}_{}_{}'.format(nr_string, b, c)] = ['nan'] * len(col)
    return nan_df

def _create_irrad_df(pv_mod, cell_pos_df):
    """Create irradiance dataframe of a module in the PV system"""
    irrad = pd.Series(pv_mod.Ee.flatten())
    irrad_df = pd.DataFrame(index=cell_pos_df.index,
                            columns=cell_pos_df.columns)
    for column in cell_pos_df.columns:
        for row in cell_pos_df.index:
            cell_index = cell_pos_df.loc[row, column]
            irrad_df.loc[row, column] = irrad[cell_index]
    return irrad_df

def _create_temp_df(pv_mod, cell_pos_df):
    """Create temperature dataframe of a module in the PV system"""
    temp = pd.Series(pv_mod.Tcell.flatten())
    temp_df = pd.DataFrame(index=cell_pos_df.index,
                           columns=cell_pos_df.columns)
    for column in cell_pos_df.columns:
        for row in cell_pos_df.index:
            cell_index = cell_pos_df.loc[row, column]
            temp_df.loc[row, column] = temp[cell_index]
    return temp_df

def system_layout_to_xls(output_xls_name, pv_sys, write_bpd_act):
    """Write an xls with worksheets of irradiance, cell temperature
    and cell index. If "write_bpd_act" is True, bypass diode activation is
    checked and on the ActiveBpd tab bypassed cells are represented with 1 and
    non-bypassed cells with 0."""
    writer = pd.ExcelWriter(output_xls_name, engine='xlsxwriter')
    workbook = writer.book
    writer.sheets['CellIndexes'] = workbook.add_worksheet('CellIndexes')
    writer.sheets['Irradiance'] = workbook.add_worksheet('Irradiance')
    writer.sheets['CellTemp'] = workbook.add_worksheet('CellTemp')
    writer.sheets['BpdAndRbc'] = workbook.add_worksheet('BpdAndRbc')
    if write_bpd_act:
        pv_sys_vmp = pv_sys.Vmp
        print(pv_sys.Pmp)
    for s, string in enumerate(pv_sys.pvstrs):
        if write_bpd_act:
            interp_string_iv = interp1d(string.Vstring, string.Istring)
            string_imp = interp_string_iv(pv_sys_vmp)
        for m, module in enumerate(string.pvmods):
            cell_pos_df = _create_cell_pos_df(pv_mod=module, nr_string=s,
                                              nr_mod=m)
            ncols = sum(module.subStrCells)
            nrows = int(module.numberCells / ncols)
            v_bpd_trig = module.Vbypass
            if write_bpd_act:
                cols_per_substr = module.subStrCells
                bpd = []
                cis = []
                rbc = []
                # checking for bypass diode activation and reverse bised cells
                for ss in range(module.numSubStr):
                    interp_substring_vi = interp1d(module.Isubstr[ss],
                                                   module.Vsubstr[ss])
                    substring_vmp = interp_substring_vi(string_imp)
                    if substring_vmp < 0: # doublecheck if we should compare to 0 here
                        [bpd.append(2) for nss in range(cols_per_substr[ss])]
                    else:
                        [bpd.append(0) for nss in range(cols_per_substr[ss])]
                    cis_inss = []
                    for col in range(cols_per_substr[ss]):
                        cis_inss += [i['idx'] for i in module.cell_pos[ss][col]]
                    cells_inss = [module.pvcells[ci] for ci in cis_inss]
                    for cell in cells_inss:
                        interp_cell_vi = interp1d(cell.Icell.flatten(),
                                                  cell.Vcell.flatten())
                        cell_vmp = interp_cell_vi(string_imp)
                        if cell_vmp < 0:
                            rbc.append(1)
                        else:
                            rbc.append(0)
                    cis += cis_inss

                cis_series = pd.Series(index=cis, data=rbc)
                bpd_df = pd.DataFrame(index=cell_pos_df.index,
                                      columns=cell_pos_df.columns)
                bpdcols = [[c] * len(bpd_df) for c in bpd]
                rbc_df = pd.DataFrame(index=cell_pos_df.index,
                                      columns=cell_pos_df.columns)
                for c, column in enumerate(cell_pos_df.columns):
                    bpd_df[column] = bpdcols[c]
                    for row in cell_pos_df.index:
                        ci = cell_pos_df.loc[row, column]
                        rbc_df.loc[row, column] = cis_series[ci]
                # merging bpd and rbc dataframes into one dataframe, where
                # 2 = bypassed cells and 1 = reverse biased cells
                bpdrbc_df = (bpd_df * 2 + rbc_df).clip(upper=2)
            # writing xls files
            if not write_bpd_act:
                bpdrbc_df = _create_nan_df(pv_mod=module, nr_string=s, nr_mod=m)
            startcol = 0 if s == 0 else s*(ncols+1)
            startrow = 0 if m == 0 else m*(nrows+1)

            cell_pos_df.to_excel(writer, sheet_name='CellIndexes',
                                 startrow=startrow , startcol=startcol)
            irrad_df = _create_irrad_df(pv_mod=module, cell_pos_df=cell_pos_df)
            irrad_df.to_excel(writer, sheet_name='Irradiance',
                              startrow=startrow, startcol=startcol)
            temp_df = _create_temp_df(pv_mod=module, cell_pos_df=cell_pos_df)
            temp_df.to_excel(writer, sheet_name='CellTemp', startrow=startrow,
                             startcol=startcol)
            bpdrbc_df.to_excel(writer, sheet_name='BpdAndRbc',
                               startrow=startrow, startcol=startcol)
    # formatting the Irradiance worksheet
    writer.sheets['Irradiance'].conditional_format(0, 0,
                                        writer.sheets['Irradiance'].dim_rowmax,
                                        writer.sheets['Irradiance'].dim_colmax,
                                        {'type': '2_color_scale',
                                         'min_type': 'num',
                                         'max_type': 'num',
                                         'min_value':0,
                                         'max_value':1,
                                         'min_color':'#808080',
                                         'max_color':'#FFD700'})
    # formatting the CellTemp worksheet
    writer.sheets['CellTemp'].conditional_format(0, 0,
                                    writer.sheets['CellTemp'].dim_rowmax,
                                    writer.sheets['CellTemp'].dim_colmax,
                                    {'type': '3_color_scale',
                                     'min_type': 'num',
                                     'mid_type': 'num',
                                     'max_type': 'num',
                                     'min_value':273.15,
                                     'mid_value':273.15 + 25,
                                     'max_value':273.15 + 85,
                                     'min_color':'#85C1E9',
                                     'mid_color':'#E5E7E9',
                                     'max_color':'#E74C3C'})
    # formatting BpdAndRbc worksheet
    writer.sheets['BpdAndRbc'].conditional_format(0, 0,
                                    writer.sheets['BpdAndRbc'].dim_rowmax,
                                    writer.sheets['BpdAndRbc'].dim_colmax,
                                    {'type': '3_color_scale',
                                     'min_type': 'num',
                                     'mid_type': 'num',
                                     'max_type': 'num',
                                     'min_value':0,
                                     'mid_value':1,
                                     'max_value':2,
                                     'min_color':'#FFFFFF',
                                     'mid_color':'#FF6347',
                                     'max_color':'#36C1FF'})
    writer.save()
    writer.close()

def set_input_from_xls(input_xls_name, pv_sys, str_num, str_len):
    """Set cell temperatures of a PVMM PV system from an xls"""
    for string in list(range(str_num)):
        for module in list(range(str_len)):
            ncols = sum(pv_sys.pvstrs[string].pvmods[module].subStrCells)
            nrows = int(pv_sys.pvstrs[string].pvmods[module].numberCells/ncols)
            irrad = pd.read_excel(input_xls_name, sheet_name='Irradiance',
                                  skiprows=module*(nrows+1),nrows=nrows,
                                  usecols=range(string*(ncols+1),
                                  (string+1)*(ncols+1)),
                                  index_col=0, header=0)
            cell_temp = pd.read_excel(input_xls_name, sheet_name='CellTemp',
                                      skiprows=module*(nrows+1), nrows=nrows,
                                      usecols=range(string*(ncols+1),
                                      (string+1)*(ncols+1)),
                                      index_col=0, header=0)
            cell_pos = pd.read_excel(input_xls_name, sheet_name='CellIndexes',
                                     skiprows=module*(nrows+1), nrows=nrows,
                                     usecols=range(string*(ncols+1),
                                     (string+1)*(ncols+1)),
                                     index_col=0, header=0)
            Ee = []
            Tc = []
            mod_cell_idxs = []
            for column in cell_pos.columns:
                for row in cell_pos.index:
                    Ee.append(irrad.loc[row, column])
                    Tc.append(cell_temp.loc[row, column])
                    mod_cell_idxs.append(cell_pos.loc[row, column])
            pv_sys.setTemps({string:{module:[Tc, mod_cell_idxs]}})
            pv_sys.setSuns({string:{module:[Ee, mod_cell_idxs]}})
