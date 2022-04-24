import streamlit as st
import pandas as pd
import numpy as np

###################################
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode


pd.set_option('precision', 2)

###################################

from functionforDownloadButtons import download_button

###################################


def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]

def _max_width_():
    max_width_str = f"max-width: 1800px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_icon="✂️", page_title="Atucha Ate - Obra Social Procesor")

# st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Asociaci%C3%B3n_Trabajadores_del_Estado.png/200px-Asociaci%C3%B3n_Trabajadores_del_Estado.png", width=100)
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Asociaci%C3%B3n_Trabajadores_del_Estado.png/200px-Asociaci%C3%B3n_Trabajadores_del_Estado.png",
    width=100,
)

st.title("Atucha Ate - Obra Social Procesor")

st.markdown("-----------")
st.markdown("#### Parametrizacion:")

precio_sb02_per_capita = st.number_input('Ingrese el monto por capita para el plan SB02', value=8325.71)

valor_capita_und = st.number_input('Ingrese el valor por capita UND', value=269, help="monto multiplicador por la cantidad de miembros para el calculo de 'Valor Cap Und'")

valor_capita_res = st.number_input('Ingrese el valor por capita RES', value=118, help="monto multiplicador por la cantidad de miembros para el calculo de 'Valor Cap Res'")

coef_final = st.number_input('Ingrese el coeficiente final para el aporte', value=1.2,  help="coeficiente multiplicador aplicado al aporte final")

st.markdown("-----------")
st.markdown("#### Carga de Factura y Nota de Credito:")


c29, c30, c31 = st.columns([1, 6, 1])


with c30:

    factura_uploaded_file = st.file_uploader(
        "",
        key="1",
        help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
    )

    if factura_uploaded_file is not None:
        factura_file_container = st.expander("Check your uploaded .csv")
        pd_factura_origin = pd.read_excel(factura_uploaded_file)
        factura_uploaded_file.seek(0)
        factura_file_container.write(pd_factura_origin)

    else:
        st.info(
            f"""
                👆 Cargue una factura.xslx primero. Muestra para probar: [factura.xslx](https://docs.google.com/spreadsheets/d/e/2PACX-1vTkO14QeW1s6OMFhSQd1XwUyERxVZ7mwiw_X7PHoXIlvGh_xYWKq4nmsCpbRjjbQg/pub?output=xlsx))
                """
        )

        st.stop()
        
        
        
    notacredito_uploaded_file = st.file_uploader(
        "",
        key="2",
        help=""
    )

    if notacredito_uploaded_file is not None:
        notacredito_file_container = st.expander("Check your uploaded .csv")
        pd_notacredito_origin = pd.read_excel(notacredito_uploaded_file)
        notacredito_uploaded_file.seek(0)
        notacredito_file_container.write(pd_notacredito_origin)

    else:
        st.info(
            f"""
                👆 Cargue una notacredito.xslx primero. Muestra para probar: [notacredito.xslx](https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2Acg3snX-xtiz-q-oe3xlO2gdMFOU-_5oXclNEnrUmNlPBdl4MdXplzZkthgPrA/pub?output=xlsx))
                """
        )

        st.stop()

from st_aggrid import GridUpdateMode, DataReturnMode

gb = GridOptionsBuilder.from_dataframe(pd_factura_origin)
# enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=False)
gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
gridOptions = gb.build()

st.success(
    f"""
        💡 Tip! Hold the shift key when selecting rows to select multiple rows at once!
        """
)

response = AgGrid(
    pd_factura_origin,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=False,
)

df_consolidado = pd.DataFrame()

df_factura_selected = pd_factura_origin
# pd.DataFrame(response["selected_rows"])

df_factura_lite = pd.DataFrame()
if df_factura_selected.empty == False:
    
    
    
    # df_factura_selected = pd.DataFrame(response["selected_rows"])
    df_factura_selected['Plan'] = df_factura_selected['Plan tarifa'].str.slice(0,4)
    df_factura_columns = ['Socio', 'Cuil', 'Nombre y apellido', 'Plan', 'Cant miembros', 'Importe exento']
    df_factura_lite = df_factura_selected[df_factura_columns]
    df_factura_lite.rename(columns = {'Importe exento':'Monto Factura'}, inplace = True)
    df_factura_lite['Monto SB02'] = df_factura_lite['Cant miembros'] * precio_sb02_per_capita
    
    df_montos_por_capita_encontrados = (df_factura_lite['Monto Factura'] / df_factura_lite['Cant miembros']).round(2).unique()
    st.markdown("> montos por capita encontrados son")
    st.table(df_montos_por_capita_encontrados)
    
    
df_merge_origin = pd.DataFrame()
df_sin_nota = pd.DataFrame()
df_consolidado = pd.DataFrame()

if pd_notacredito_origin.empty == False:
    df_notacredito_columns = ['Socio', 'Importe exento']
    df_notacredito_lite = pd_notacredito_origin[df_notacredito_columns]
    df_notacredito_lite.rename(columns = {'Importe exento':'Monto Credito'}, inplace = True)
    
    df_merge_origin = df_factura_lite.merge(df_notacredito_lite, on='Socio', how='left')
    df_sin_nota = df_merge_origin[pd.isnull(df_merge_origin['Monto Credito'])]
    df_consolidado = df_merge_origin[~pd.isnull(df_merge_origin['Monto Credito'])]
    df_consolidado['Dif Emitida'] = df_consolidado['Monto Credito'] - df_consolidado['Monto Factura']
    df_consolidado['Dif SB02'] = df_consolidado['Monto Credito'] - df_consolidado['Monto SB02']
    df_consolidado['Dif Capital'] = df_consolidado['Monto Factura'] - df_consolidado['Monto SB02']
    df_consolidado['Valor Cap Und'] = df_consolidado['Cant miembros'] * valor_capita_und
    df_consolidado['Valor Cap Res'] = df_consolidado['Cant miembros'] * valor_capita_res
    df_consolidado['Aporte Lineal'] = df_consolidado['Dif Capital'] +  df_consolidado['Valor Cap Und'] +  df_consolidado['Valor Cap Res']
    df_consolidado['Aporte Final'] = df_consolidado['Aporte Lineal'] * coef_final
    df_consolidado = df_consolidado.round(2)

    
    gb_sin_nota = GridOptionsBuilder.from_dataframe(df_sin_nota)
    # enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
    gb_sin_nota.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb_sin_nota.configure_selection(selection_mode="multiple", use_checkbox=False)
    gb_sin_nota.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
    gridSinNotaOptions = gb_sin_nota.build()

    st.error(
        f"""
            💡 Beneficiarios sin nota de credito ! Estos nos se procesaran en el consolidado !
            """
    )

    responseSinNota = AgGrid(
        df_sin_nota,
        gridOptions=gridSinNotaOptions,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
    )
    
    gb_consolidado = GridOptionsBuilder.from_dataframe(df_consolidado)
    # enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
    gb_consolidado.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb_consolidado.configure_selection(selection_mode="multiple", use_checkbox=False)
    gb_consolidado.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
    gridConsolidadoOptions = gb_consolidado.build()


    st.success(
        f"""
            💡 Consolidado de Beneficiarios ! Es una vista previa del consolidado generado!
            """
    )


    responseConsolidado = AgGrid(
        df_consolidado,
        gridOptions=gridConsolidadoOptions,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
    )
    

st.subheader("Una descripcion estadistica de los datos consolidados 👇")
st.info(
    f"""
        💡  Con primer vistazo, puede ser util para ver numeros maximos que no tengan sentido
        """
)
st.text("")
st.dataframe(df_consolidado.describe())


st.subheader("Los datos consolidados aparecerán debajo 👇")
st.text("")


# format_dict = {'sum':'${0:,.0f}', 'date': '{:%m-%Y}', 'pct_of_total': '{:.2%}'}
# st.dataframe(df_consolidado.style.applymap(color_negative_red))


st.dataframe(df_consolidado)

st.text("")

c29, c30, c31 = st.columns([1, 1, 2])


with c30:

    df_consolidado.to_excel('consolidado.xlsx', index=False)
    with open("consolidado.xlsx", "rb") as file:
        btn = st.download_button(
             label="Descargar Consolidado",
             data=file,
             file_name="consolidado.xlsx"
        )
