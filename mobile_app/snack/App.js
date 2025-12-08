import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, Alert, ScrollView, StyleSheet } from 'react-native';
import axios from 'axios';

// --- CONFIG ---
// Using your Render deployment URL. This is the API base the Snack app will call.
// Make sure it ends with `/api/`.
const API_BASE = 'https://peitel1-final-backend-psru.onrender.com/api/';

// Simple axios client
const client = axios.create({ baseURL: API_BASE, timeout: 15000, headers: { Accept: 'application/json' } });

export default function App(){
  const [screen, setScreen] = useState('login');
  const [token, setToken] = useState(null);

  // login fields
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // POS state
  const [services, setServices] = useState([]);
  const [quantities, setQuantities] = useState({});
  const [patient, setPatient] = useState({ first_name:'', last_name:'', contact_number:'', email:'', address:'' });

  useEffect(()=>{
    if(token){
      client.defaults.headers.common['Authorization'] = `Token ${token}`;
      loadServices();
    }
  },[token]);

  async function onLogin(){
    if(!username || !password) return Alert.alert('Validation','Enter username & password');
    try{
      const res = await client.post('auth/login/', { username, password });
      if(res && res.data){
        const payload = res.data;
        // API returns token and user details. Ensure account is staff and approved
        const user = payload.user || {};
        const isStaff = user.is_staff === true;
        const isApproved = (user.is_approved === true) || (user.is_active === true && (user.is_staff === true));
        if(!isStaff){
          return Alert.alert('Access denied', 'Account is not a staff account.');
        }
        if(!isApproved){
          return Alert.alert('Pending approval', 'Your account is not yet approved by the admin. Please wait for approval.');
        }
        if(payload.token){
          setToken(payload.token);
          setScreen('pos');
          return;
        }
      }
      Alert.alert('Login failed', JSON.stringify(res.data || res));
    }catch(e){
      const msg = e?.response?.data?.error || e?.message || JSON.stringify(e);
      Alert.alert('Login error', msg);
    }
  }

  async function loadServices(){
    try{
      const res = await client.get('services/');
      setServices(res.data || []);
    }catch(e){
      console.warn('services error', e);
      Alert.alert('Error','Failed to load services');
    }
  }

  function changeQty(id, val){
    const q = parseInt(val) || 0;
    setQuantities(prev=> ({ ...prev, [id]: q }));
  }

  async function createInvoice(){
    const totalQty = Object.values(quantities).reduce((s,v)=>s + (v||0), 0);
    if(totalQty === 0) return Alert.alert('Validation','Choose at least one service');
    try{
      const p = await client.post('patients/', patient);
      if(!p || !p.data || !p.data.id) return Alert.alert('Error','Failed to create patient');
      const servicesPayload = services.map(s=>({ service: s.id, quantity: quantities[s.id] || 0 })).filter(x=> x.quantity>0);
      const inv = await client.post('invoices/', { patient: p.data.id, services: servicesPayload });
      Alert.alert('Success', `Invoice #${inv.data?.id || 'created'}`);
    }catch(e){
      const msg = e?.response?.data?.error || e?.message || JSON.stringify(e);
      Alert.alert('Error', msg);
    }
  }

  if(screen === 'login'){
    return (
      <View style={styles.center}>
        <Text style={styles.title}>Staff Login</Text>
        <TextInput placeholder="Username" style={styles.input} value={username} onChangeText={setUsername} autoCapitalize="none" />
        <TextInput placeholder="Password" style={styles.input} value={password} onChangeText={setPassword} secureTextEntry />
        <Button title="Login" onPress={onLogin} />
        <Text style={styles.note}>Make sure staff account is approved in admin.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Staff POS</Text>

      <Text style={styles.section}>Patient</Text>
      <TextInput placeholder="First name" style={styles.input} value={patient.first_name} onChangeText={(t)=>setPatient(p=>({...p, first_name:t}))} />
      <TextInput placeholder="Last name" style={styles.input} value={patient.last_name} onChangeText={(t)=>setPatient(p=>({...p, last_name:t}))} />
      <TextInput placeholder="Contact" style={styles.input} value={patient.contact_number} onChangeText={(t)=>setPatient(p=>({...p, contact_number:t}))} />
      <TextInput placeholder="Email" style={styles.input} value={patient.email} onChangeText={(t)=>setPatient(p=>({...p, email:t}))} />

      <Text style={styles.section}>Services</Text>
      {services.map(s=> (
        <View key={s.id} style={styles.row}>
          <View style={{flex:1}}>
            <Text style={{fontWeight:'600'}}>{s.name}</Text>
            <Text style={{color:'#666'}}>₱{s.price}</Text>
          </View>
          <TextInput keyboardType="numeric" style={styles.qty} value={(quantities[s.id]||'').toString()} onChangeText={(v)=>changeQty(s.id, v)} />
        </View>
      ))}

      <Button title="Create Invoice" onPress={createInvoice} />
      <View style={{height:30}} />
      <Button title="Logout" onPress={()=>{ setToken(null); setScreen('login'); client.defaults.headers.common['Authorization'] = undefined; }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center:{ flex:1, padding:20, justifyContent:'center' },
  container:{ padding:12 },
  title:{ fontSize:22, fontWeight:'700', marginBottom:12 },
  input:{ borderWidth:1, borderColor:'#ccc', padding:8, borderRadius:8, marginBottom:8 },
  note:{ color:'#666', marginTop:8, fontSize:12 },
  section:{ fontSize:18, marginTop:12, marginBottom:6 },
  row:{ flexDirection:'row', alignItems:'center', paddingVertical:8, borderBottomWidth:1, borderBottomColor:'#eee' },
  qty:{ width:80, borderWidth:1, borderColor:'#ddd', padding:6, borderRadius:6 }
});
