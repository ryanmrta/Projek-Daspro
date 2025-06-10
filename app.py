from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Koordinat kost (latitude, longitude)
KOST_COORDINATES = {
    'Kost Yunawan': (-7.414144449056151, 109.33963472475938),
    'Kost Morena 2': (-7.41670886311937, 109.33873370289292),
    'Kost Wisma Soedirman': (-7.425553599806565, 109.33506904737877),
    'Kost Fikal': (-7.425583854300968, 109.3352308112676),
    'Kost Krikil': (-7.428498461723705, 109.3409119959236),
    'Kost Harmoni': (-7.424408448651367, 109.33990548574282),
    'Kost Wisma Aisyah': (-7.428115034067173, 109.34138593141536),
    'Kost Mawar Sehati': (-7.414336421443232, 109.33808371922774),
    'Kost Haykal': (-7.431797557153211, 109.34031812475959),
    'Kost Wisma Pink': (-7.425482759974732, 109.33491982475948),
    'Fila Kost': (-7.422234497434835, 109.33777074715977),
    'Wisma Alden Bu Ning': (-7.429131328393767, 109.33945592900302)
}

def get_db_connection():
    conn = sqlite3.connect('kost.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Create kost table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS kost (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            price TEXT NOT NULL,
            type TEXT NOT NULL,
            facilities TEXT NOT NULL,
            kontak TEXT NOT NULL,
            image1 TEXT,
            image2 TEXT,
            image3 TEXT,
            page INTEGER NOT NULL
        )
    ''')
    
    # Check if data already exists
    existing_data = conn.execute('SELECT COUNT(*) FROM kost').fetchone()[0]
    
    if existing_data == 0:
        # Insert data from index2.html (page 1)
        kost_data_page1 = [
            ('Kost Yunawan', 'Jl. Mawar No.5, Dusun 2, Kalimanah Wetan, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 6jt', 'Khusus Cowo', 'WiFi,Kamar Mandi Dalam,AC,Parkir', '0838-0678-9040', 'kostyunawan1.jpg', 'kostyunawan2.jpg', 'kostyunawan3.jpg', 1),
            ('Kost Morena 2', 'Jl. Menur Dusun No.2, RT.03/RW.07, Dusun 2, Kalimanah Wetan, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 4.5jt', 'Khusus Cewe', 'WiFi,Kamar Mandi Dalam,Security 24 Jam', '0812-3846-5842','kostmorena1.png', 'kostmorena2.png', 'kostmorena3.png', 1),
            ('Kost Wisma Soedirman', 'Dusun 2, Blater, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 7jt', 'Khusus Cowo', 'WiFi,AC,Kamar Mandi Dalam,Parkir', '0858-5184-5579', 'kostwisud.jpg', 'kostwisud2.jpg', 'kostwisud3.jpg', 1)
        ]
        
        # Insert data from kostpage2.html (page 2)
        kost_data_page2 = [
            ('Kost Fikal', 'Dusun 2, Blater, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 7.5jt', 'Khusus Cowo', 'WiFi,Security 24 Jam,AC,Dapur Bersama,Parkir Motor', '0813-8499-9986', 'kostfikal2.jpg', 'kostfikal1.jpg', 'kostfikal3.jpg', 2),
            ('Kost Krikil', 'Unnamed Road, Dusun 2, Sidakangen, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 3.5jt', 'Campur', 'WiFi,AC,Dapur Bersama,Valet Parking', '0838-5142-0015', 'kostkerikil1.jpg', 'kostkerikil2.jpg', 'kostkerikil3.jpg', 2),
            ('Kost Harmoni', 'Sidakangen RT 01 RW 1 NO 2, Kabupaten Purbalingga, Jawa Tengah', 'Rp 8jt', 'Khusus Cowo', 'WiFi,AC,Dapur Bersama,Kamar Mandi Dalam,Parkir Motor', '0858-0320-1098', 'kostharmoni1.png', 'kostharmoni2.png', 'kostharmoni3.png', 2),
            ('Kost Wisma Aisyah', 'Dusun 2, Sidakangen, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 4jt', 'Khusus Cewe', 'WiFi,AC,Kipas Angin,Dapur Bersama', '0899-5048-134', 'wismaaisyah1.png', 'wismaaisyah2.jpeg', 'wismaaisyah3.jpeg', 2),
            ('Kost Mawar Sehati', 'Jl. Mawar, Dusun 1, Kalimanah Wetan, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 5.4jt', 'Khusus Cowo', 'WiFi,Kipas Angin,Parkir,Kamar Mandi Dalam', '0835-1458-8848', 'kostmawarsehati1.jpg', 'kostmawarsehati2.jpg', 'kostmawarsehati3.jpg', 2),
            ('Kost Haykal', 'Dusun 1, Blater, Kalimanah, Purbalingga Regency, Central Java 53371', 'Rp 5jt', 'Khusus Cowo', 'WiFi,Kamar Mandi Dalam,Security,Parkir Motor', '0818-2548-3360', 'haykal1.jpeg', 'haykal2.jpeg', 'haykal3.jpeg', 2),    
            ('Kost Wisma Pink', 'Jl. Raya Mayjen Sungkono No.9a, Dusun 2, Sidakangen, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 5.5jt', 'Khusus Cewe', 'WiFi,Kipas Angin,Kasur,Parkir Motor', '0844-1441-8888', 'wismapink1.png', 'wismapink2.png', 'wismapink3.png', 2),
            ('Fila Kost', 'Blater 003/007 No. 42, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 4.8jt', 'Campur', 'WiFi,AC,Kamar Mandi Dalam,Security,Parkir', '0884-7747-3600', 'filakost1.png', 'filakost2.png', 'filakost3.jpg', 2),
            ('Wisma Alden Bu Ning', 'JDusun 2, Blater, Kec. Kalimanah, Kabupaten Purbalingga, Jawa Tengah', 'Rp 5jt', 'Khusus Cewe', 'WiFi,Kipas Angin,Dapur,Parkir Motor', '0888-1101-9893', 'wismaalden1.png', 'wismaalden2.png', 'wismaalden3.png', 2)
        ]
        
        all_kost_data = kost_data_page1 + kost_data_page2
        
        conn.executemany('''
            INSERT INTO kost (name, address, price, type, facilities, kontak, image1, image2, image3, page)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', all_kost_data)
        
        conn.commit()
    
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/tentangkami')
def tentangkami():
    return render_template('tentangkami.html')

@app.route('/api/search')
def search_kost():
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'results': [], 'count': 0})
    
    conn = get_db_connection()
    
    # Search in both name and address fields
    results = conn.execute('''
        SELECT * FROM kost 
        WHERE LOWER(name) LIKE LOWER(?) 
        OR LOWER(address) LIKE LOWER(?)
        ORDER BY name
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    
    # Convert results to list of dictionaries
    kost_list = []
    for row in results:
        kost_list.append({
            'id': row['id'],
            'name': row['name'],
            'address': row['address'],
            'price': row['price'],
            'type': row['type'],
            'facilities': row['facilities'].split(','),
            'kontak': row['kontak'],
            'images': [row['image1'], row['image2'], row['image3']],
            'page': row['page']
        })
    
    return jsonify({
        'results': kost_list,
        'count': len(kost_list),
        'query': query
    })

@app.route('/api/kost')
def get_all_kost():
    page = request.args.get('page', type=int)
    
    conn = get_db_connection()
    
    if page:
        results = conn.execute('SELECT * FROM kost WHERE page = ? ORDER BY name', (page,)).fetchall()
    else:
        results = conn.execute('SELECT * FROM kost ORDER BY name').fetchall()
    
    conn.close()
    
    # Convert results to list of dictionaries
    kost_list = []
    for row in results:
        kost_list.append({
            'id': row['id'],
            'name': row['name'],
            'address': row['address'],
            'price': row['price'],
            'type': row['type'],
            'facilities': row['facilities'].split(','),
            'kontak': row['kontak'],
            'images': [row['image1'], row['image2'], row['image3']],
            'page': row['page']
        })
    
    return jsonify({
        'results': kost_list,
        'count': len(kost_list)
    })
    
@app.route('/map/<kost_name>')
def show_map(kost_name):
    # Get kost data
    conn = get_db_connection()
    kost = conn.execute('SELECT * FROM kost WHERE name = ?', (kost_name,)).fetchone()
    conn.close()
    
    if not kost:
        return "Kost tidak ditemukan", 404
    
    # Get coordinates
    coordinates = KOST_COORDINATES.get(kost_name)
    if not coordinates:
        return "Koordinat tidak tersedia", 404
    
    kost_data = {
        'name': kost['name'],
        'address': kost['address'],
        'price': kost['price'],
        'type': kost['type'],
        'facilities': kost['facilities'].split(','),
        'kontak': kost['kontak'],
        'images': [kost['image1'], kost['image2'], kost['image3']],
        'lat': coordinates[0],
        'lng': coordinates[1]
    }
    
    return render_template('map.html', kost=kost_data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
