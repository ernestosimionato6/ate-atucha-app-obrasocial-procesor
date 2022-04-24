import streamlit as st
import pandas as pd
import numpy as np

###################################
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

###################################

from functionforDownloadButtons import download_button

###################################


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

# st.image("https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/balloon_1f388.png", width=100)
st.image(
    "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/scissors_2702-fe0f.png",
    width=100,
)

st.title("Atucha Ate - Obra Social Procesor")

st.markdown("-----------")
st.markdown("#### Parametrizacion:")

precio_sb02_per_capita = st.number_input('Ingrese el monto por capita para el plan SB02', value=8325.71)


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
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
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



df_factura_selected = pd.DataFrame(response["selected_rows"])

df_factura_lite = pd.DataFrame()
if df_factura_selected.empty == False:
    
    
    
    # df_factura_selected = pd.DataFrame(response["selected_rows"])
    df_factura_selected['Plan'] = df_factura_selected['Plan tarifa'].str.slice(0,4)
    df_factura_columns = ['Socio', 'Cuil', 'Nombre y apellido', 'Plan', 'Cant miembros', 'Importe exento']
    df_factura_lite = df_factura_selected[df_factura_columns]
    df_factura_lite.rename(columns = {'Importe exento':'Monto Factura'}, inplace = True)
    df_factura_lite['Monto SB02'] = (df_factura_lite['Cant miembros'] * precio_sb02_per_capita).round()
    
    df_montos_por_capita_encontrados = (df_factura_lite['Factura Emitida'] / df_factura_lite['Cant miembros']).round(1).unique()
    st.markdown("> montos por capita encontrados son" + df_montos_por_capita_encontrados)
    
    
df_merge_origin = pd.DataFrame()
df_sin_nota = pd.DataFrame()
df_consolidado = pd.DataFrame()

if pd_notacredito_origin.empty == False:
    df_notacredito_columns = ['Socio', 'Importe exento']
    df_notacredito_lite = pd_notacredito_origin[df_notacredito_columns]
    df_notacredito_lite.rename(columns = {'Importe exento':'Monto Credito'}, inplace = True)
    
    df_merge_origin = df_factura_lite.merge(df_notacredito_lite, on='Socio', how='left')
    df_sin_nota = df_merge_origin[~pd.isnull(df_merge_origin['Monto Credito'])]
    df_consolidado = df_merge_origin[pd.isnull(df_merge_origin['Monto Credito'])]
    


    
    gb_sin_nota = GridOptionsBuilder.from_dataframe(df_sin_nota)
    # enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
    gb_sin_nota.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb_sin_nota.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb_sin_nota.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
    gridSinNotaOptions = gb_sin_nota.build()

    st.success(
        f"""
            💡 Tip! Hold the shift key when selecting rows to select multiple rows at once!
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
    gb_consolidado.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb_consolidado.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
    gridConsolidadoOptions = gb_consolidado.build()

    st.success(
        f"""
            💡 Tip! Hold the shift key when selecting rows to select multiple rows at once!
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
    

st.subheader("Filtered data will appear below 👇 ")
st.text("")

st.table(df_factura_lite)

    
st.text("")

c29, c30, c31 = st.columns([1, 1, 2])


with c30:

    df_factura_lite.to_excel('consolidado.xlsx', index=False)
    with open("consolidado.xlsx", "rb") as file:
        btn = st.download_button(
             label="Descargar Consolidado",
             data=file,
             file_name="consolidado.xlsx"
        )
