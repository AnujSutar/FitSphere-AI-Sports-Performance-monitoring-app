import pandas as pd
import streamlit as st
from database.connection import connect,init_db
from pathlib import Path

def ensure_products():
    init_db()
    with connect() as c:
        if c.execute('SELECT COUNT(*) FROM shop_products').fetchone()[0]==0:
            path=Path(__file__).resolve().parents[1]/'data'/'sample_products.csv'
            for r in pd.read_csv(path).to_dict('records'):
                c.execute("INSERT INTO shop_products(name,category,description,price,unit,tag) VALUES(?,?,?,?,?,'Synthetic demo')",(r['name'],r['category'],r['description'],float(r['price_inr']),r['unit']))

def marketplace_page():
    ensure_products(); uid=st.session_state.user_id
    st.markdown("<div class='eyebrow'>FITSPHERE MARKETPLACE</div><h1>Gear up for your goals</h1>",unsafe_allow_html=True)
    st.caption('Starter catalog items are marked demo. Sellers can publish their own listings. Checkout creates a local demo order only; no payment is taken.')
    with st.expander('Sell on FitSphere · Add a product'):
        with st.form('seller_add_product',clear_on_submit=True):
            name=st.text_input('Product name'); category=st.selectbox('Category',['Protein & nutrition','Gym equipment','Accessories','Healthy snacks']); description=st.text_area('Description'); price=st.number_input('Price (₹)',min_value=1.0,value=499.0,step=50.0); unit=st.text_input('Pack size / unit',value='1 piece'); publish=st.checkbox('I confirm this is an accurate listing and price.')
            if st.form_submit_button('Publish listing'):
                if not name.strip() or not description.strip(): st.error('Enter a product name and description.')
                elif not publish: st.error('Confirm the listing details before publishing.')
                else:
                    with connect() as c: c.execute("INSERT INTO shop_products(name,category,description,price,unit,tag,seller_id) VALUES(?,?,?,?,?,'Seller listing',?)",(name.strip(),category,description.strip(),price,unit.strip(),uid))
                    st.success('Your product is live in this local marketplace.'); st.rerun()
    with connect() as c: products=pd.read_sql_query('SELECT * FROM shop_products',c); cart=pd.read_sql_query('SELECT c.product_id,c.quantity,p.name,p.price FROM shop_cart c JOIN shop_products p ON p.id=c.product_id WHERE c.user_id=?',c,params=(uid,)); saved=pd.read_sql_query('SELECT product_id FROM shop_wishlist WHERE user_id=?',c,params=(uid,))
    a,b,c=st.columns(3); a.metric('Demo products',len(products)); b.metric('Cart items',int(cart.quantity.sum()) if len(cart) else 0); c.metric('Saved items',len(saved))
    with connect() as db: own=pd.read_sql_query('SELECT id,name,price,unit FROM shop_products WHERE seller_id=?',db,params=(uid,))
    if not own.empty:
        with st.expander(f'My seller listings · {len(own)}'):
            st.dataframe(own,hide_index=True,use_container_width=True)
            listing_id=st.selectbox('Choose your listing',own.id,format_func=lambda x:own.loc[own.id==x,'name'].iloc[0],key='seller_manage')
            full=products[products.id==listing_id].iloc[0]
            with st.form('seller_edit'):
                new_name=st.text_input('Edit product name',full['name']); new_desc=st.text_area('Edit description',full['description']); new_price=st.number_input('Edit price (₹)',min_value=1.,value=float(full['price']),step=50.)
                if st.form_submit_button('Save listing edits'):
                    with connect() as db: db.execute('UPDATE shop_products SET name=?,description=?,price=? WHERE id=? AND seller_id=?',(new_name.strip(),new_desc.strip(),new_price,int(listing_id),uid))
                    st.rerun()
            confirm_remove=st.checkbox('Confirm removal of my listing',key='seller_confirm_remove')
            if st.button('Remove my listing',disabled=not confirm_remove):
                with connect() as db: db.execute('DELETE FROM shop_products WHERE id=? AND seller_id=?',(int(listing_id),uid))
                st.rerun()
    q,cat,sort=st.columns([2,1,1]); term=q.text_input('Search products'); cats=['All categories']+sorted(products.category.unique()); category=cat.selectbox('Category',cats); order=sort.selectbox('Sort by',['Featured','Price: low to high','Price: high to low'])
    view=products.copy()
    if term: view=view[view.name.str.contains(term,case=False)|view.description.str.contains(term,case=False)]
    if category!='All categories': view=view[view.category==category]
    if order=='Price: low to high': view=view.sort_values('price')
    if order=='Price: high to low': view=view.sort_values('price',ascending=False)
    cols=st.columns(3)
    for i,(_,p) in enumerate(view.iterrows()):
        with cols[i%3]:
            with st.container(border=True):
                st.markdown(f"#### {p['name']}"); st.caption(f"{p['category']} · {p['unit']} · {p['tag']}")
                st.write(p['description']); st.markdown(f"### ₹{p['price']:.0f}")
                left,right=st.columns(2)
                if left.button('Add to cart',key=f"cart_{p.id}",use_container_width=True):
                    with connect() as c: c.execute('INSERT INTO shop_cart(user_id,product_id,quantity) VALUES(?,?,1) ON CONFLICT(user_id,product_id) DO UPDATE SET quantity=quantity+1',(uid,int(p.id)))
                    st.rerun()
                saved_ids=saved.product_id.tolist()
                if right.button('♥ Saved' if p.id in saved_ids else '♡ Wishlist',key=f"wish_{p.id}",use_container_width=True):
                    with connect() as c:
                        if p.id in saved_ids: c.execute('DELETE FROM shop_wishlist WHERE user_id=? AND product_id=?',(uid,int(p.id)))
                        else: c.execute('INSERT OR IGNORE INTO shop_wishlist VALUES(?,?)',(uid,int(p.id)))
                    st.rerun()
    st.divider(); st.subheader('Your demo cart')
    if cart.empty: st.info('Your cart is empty.')
    else:
        cart['line_total']=cart.price*cart.quantity; st.dataframe(cart[['name','quantity','price','line_total']],hide_index=True,use_container_width=True); st.metric('Demo subtotal',f"₹{cart.line_total.sum():,.0f}")
        pids=cart.product_id.tolist(); remove=st.selectbox('Remove item',pids,format_func=lambda x:cart.loc[cart.product_id==x,'name'].iloc[0],key='remove_cart')
        if st.button('Remove from cart'):
            with connect() as c: c.execute('DELETE FROM shop_cart WHERE user_id=? AND product_id=?',(uid,int(remove)))
            st.rerun()
        if st.button('Place demo order',type='primary'):
            with connect() as c:
                cur=c.execute("INSERT INTO shop_orders(user_id,subtotal,status) VALUES(?,?,'Demo order — not paid')",(uid,float(cart.line_total.sum())))
                for item in cart.itertuples(): c.execute('INSERT INTO shop_order_items(order_id,product_name,quantity,unit_price) VALUES(?,?,?,?)',(cur.lastrowid,item.name,int(item.quantity),float(item.price)))
                c.execute('DELETE FROM shop_cart WHERE user_id=?',(uid,))
            st.success(f'Demo order #{cur.lastrowid} saved locally. No payment was processed.'); st.rerun()
    with connect() as c: orders=pd.read_sql_query('SELECT id,subtotal,status,created_at FROM shop_orders WHERE user_id=? ORDER BY id DESC LIMIT 10',c,params=(uid,))
    if not orders.empty:
        with st.expander('Recent demo orders'): st.dataframe(orders,hide_index=True,use_container_width=True)
