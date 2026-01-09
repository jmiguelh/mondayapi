import streamlit as st
from ldap3 import Server, Connection, ALL, SUBTREE

# Configurações do LDAP
LDAP_URL = "ldap://10.100.1.111"
LDAP_DOMAIN = "corp.com.br"
LDAP_SEARCH_BASE = "ou=Usuarios,ou=Unidades de Costura,ou=Grupo Lunelli,dc=corp,dc=com,dc=br,dc=lunelli"
LDAP_SEARCH_BASE2 = "DC=corp,DC=com,DC=br,dc=lunelli"


def _to_username(u: str) -> str:
    # Normaliza de forma consistente
    return u.strip().casefold()


def authenticate_ldap(username: str, password: str) -> bool:
    """
    Tenta bind no AD usando userPrincipalName (username@DOMAIN). Retorna True se bind for bem-sucedido.
    """
    username = _to_username(username)

    user_dn = f"{username}@{LDAP_DOMAIN}"
    server = Server(LDAP_URL, get_info=ALL)
    conn = Connection(server, user=user_dn, password=password, auto_bind=False)
    try:
        conn.open()
        conn.bind()
        return conn.bound
    finally:
        conn.unbind()


def fetch_user_info(username: str) -> dict | None:
    """
    Busca atributos displayName e mail para enriquecer a resposta após autenticação.
    """
    server = Server(LDAP_URL, get_info=ALL)
    conn = Connection(server, auto_bind=True)
    username = f"{_to_username(username)}@{LDAP_DOMAIN}"
    try:
        if not conn.bound:
            raise Exception(conn.result)
        conn.search(
            search_base=LDAP_SEARCH_BASE,
            search_filter=f"(userPrincipalName={username})",
            search_scope=SUBTREE,
            attributes=["displayName", "mail"],
        )
        if conn.entries:
            entry = conn.entries[0]
            return {"displayName": entry.displayName.value, "mail": entry.mail.value}
        return "não achei nada"
    finally:
        conn.unbind()


def login():
    with st.form("my_form"):
        username = st.text_input("Login")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == "" or password == "":
                st.error("Usuário e senha devem ser preenchidos.")
                return None
            if authenticate_ldap(username, password):
                # st.write(fetch_user_info(username))
                return username
            else:
                st.error("Usuário ou senha inválidos.")
                return None


def logout():
    if "access_token" in st.session_state:
        del st.session_state["access_token"]
        st.info("Logout realizado!", icon="ℹ️")


if __name__ == "__main__":
    if "access_token" not in st.session_state:
        usuario = login()
        if usuario is not None:
            st.session_state["access_token"] = usuario
            st.rerun()
