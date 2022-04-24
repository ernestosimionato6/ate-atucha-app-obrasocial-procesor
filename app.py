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
st.table(df_factura_selected)

if df_factura_selected is not None:
    # df_factura_selected = pd.DataFrame(response["selected_rows"])
    df_factura_selected['Plan'] = df_factura_selected['Plan tarifa'].str.slice(0,4)
    df_factura_columns = ['Socio', 'Cuil', 'Nombre y apellido', 'Plan', 'Cant miembros', 'Importe exento']
    df_factura_lite = df_factura_selected[df_factura_columns]
    df_factura_lite.rename(columns = {'Importe exento':'Factura Emitida'}, inplace = True)


    st.subheader("Filtered data will appear below 👇 ")
    st.text("")

    st.table(df_factura_lite)

    
st.text("")

c29, c30, c31 = st.columns([1, 1, 2])

with c29:

    CSVButton = download_button(
        df_factura_lite,
        "factura_preprocesada.csv",
        "Download to CSV",
    )

with c30:
    CSVButton = download_button(
        df_factura_lite,
        "factura_preprocesada.csv",
        "Download to TXT",
    )
