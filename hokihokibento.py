import pandas as pd
from sqlalchemy import create_engine
import datetime

engine = create_engine(
    "mysql+mysqlconnector://root:abc123@localhost/hokihokibento?host=localhost?port=3306")

conn = engine.connect()

results = conn.execute("SELECT * from product").fetchall()
dfProduct = pd.DataFrame(results, columns=results[0].keys())

def MainMenu() :
    return int(input("\n\nMain Menu : \n 1. Lihat Menu \n 2. Lihat Cart \n 3. Checkout \n 4. Lihat History \n 5. Keluar \n\nPilih : "))

def LihatMenu() :
    print('Menu : ')
    print(dfProduct)
    pesan = input("Input 1 untuk pesan atau input apapun untuk tidak : ")
    if(pesan == "1") :
        productId = int(input("Masukkan id product yang diinginkan : "))
        qty = int(input("Quantity : "))
        results = conn.execute("SELECT id from cart where productId={}".format(productId)).fetchall()
        if(len(results) == 0) :
            conn.execute("INSERT INTO cart VALUES(NULL, {},{})".format(productId,qty))
            print('Product berhasil masuk Cart!')
        else :
            conn.execute("UPDATE cart SET qty = {} where productId = {}".format(qty,productId))
            print('Update Cart Quantity Success!')

def LihatCart() :
    results = conn.execute("SELECT nama as Nama, harga as Harga, qty as Quantity from cart c join product p on c.productId = p.id").fetchall()
    if(len(results) > 0) :
        dfCart = pd.DataFrame(results, columns=results[0].keys())
        print("Isi Cart : ")
        print(dfCart)
    else :
        print('Isi cart kosong.')

def CheckOut() :
    results = conn.execute("SELECT p.id, nama as Nama, harga as Harga, qty as Quantity from cart c join product p on c.productId = p.id").fetchall()
    if(len(results) > 0) :
        dfPesanan = pd.DataFrame(results, columns=results[0].keys())
        print('List Pesanan : ')
        print(dfPesanan[['Nama','Harga','Quantity']])
        duit = int(input('\nTotal Harga : Rp. {} \n\nDuit anda : '.format(sum(dfPesanan['Harga'] * dfPesanan['Quantity']))))
        if(duit >= sum(dfPesanan['Harga'] * dfPesanan['Quantity'])) :
            nama = input("Nama anda ? : ")
            results = conn.execute("INSERT INTO transaction VALUES(NULL,'{}',{},{},'{}')".format(datetime.datetime.now().isoformat(), sum(dfPesanan['Harga'] * dfPesanan['Quantity']), duit, nama))
            for row in dfPesanan.values :
                conn.execute("INSERT INTO transactionitem VALUES(NULL, {},{},{},{})".format(row[0], row[2], row[3], results.lastrowid))
            conn.execute("TRUNCATE cart")
            print('Terima kasih sudah membeli {}!'.format(nama))
        else :
            print('Maaf Duit Anda Kurang')
    else :
        print('Anda belum pesan apapun')

def History() :
    print('List History Transaksi : ')
    results = conn.execute("SELECT * from transaction").fetchall()
    if(len(results) > 0) :
        dfTransaction = pd.DataFrame(results, columns=results[0].keys())
        print(dfTransaction)
        lihat = input("Input 1 untuk lihat detail atau input apapun untuk tidak : ")
        if(lihat == "1") :
            transId = input("Input id transaction : ")
            results = conn.execute("""SELECT transactionId, productId, p.nama as 'Nama Product', 
                                    ti.harga, qty, (ti.harga * qty) as 'Total Harga' 
                                    from transactionitem ti 
                                    join product p on ti.productId = p.id
                                    where transactionId = {}""".format(transId)).fetchall()
            dfTransactionItem = pd.DataFrame(results, columns=results[0].keys())
            print(dfTransactionItem)
    else : 
        print('Belum ada history transaksi')


menus = [LihatMenu,LihatCart,CheckOut,History]

while (True) :
    pilihan = MainMenu()
    if(pilihan == 5) :
        break
    else :
        menus[pilihan-1]()

