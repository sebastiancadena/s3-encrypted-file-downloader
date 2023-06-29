import pyzipper
import requests
import streamlit as st
import io
import os
import tempfile
import zipfile

def get_data(url, password):
    # Download the zip to a temporary location
    r = requests.get(url)
    # Save the zip content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(r.content)
        temp_file_path = temp_file.name

    # Decrypt the zip and generate a new zip file without a password
    with pyzipper.AESZipFile(temp_file_path) as zf:
        zf.pwd = password.encode()
        # Extract the decrypted zip file to a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zf.extractall(temp_dir)

            # Compress the extracted files into a new zip file
            with io.BytesIO() as compressed_zip:
                with zipfile.ZipFile(compressed_zip, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            new_zip.write(file_path, arcname=os.path.relpath(file_path, temp_dir))
                data = compressed_zip.getvalue()
    # Delete the temporary file
    if temp_file_path:
        os.remove(temp_file_path)
    return data

st.set_page_config(layout="wide", page_title='Utilidad para desencriptar archivos cifrados')
params = st.experimental_get_query_params()

with st.form(key='download_form'):
    url = st.text_input(label='Enlace de descarga del archivo cifrado', value=params.get('s3_url', [''])[0])
    password = st.text_input(label='Contraseña', type='password', value=params.get('password', [''])[0])
    submitted = st.form_submit_button(label='Desencriptar')

    if submitted:
        if 'raw_zip' in st.session_state:
            del st.session_state.raw_zip
        st.session_state.raw_zip = get_data(url, password)

if 'raw_zip' in st.session_state:
    st.download_button(label="Descargar", data=st.session_state.raw_zip,
                        file_name='test_results.zip',
                        mime='application/zip')

