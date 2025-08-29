'use client'
import { useState } from 'react'
import { login } from '@/lib/api'


export default function Login(){
 const [u,setU]=useState('admin');
 const [p,setP]=useState('admin');
 const submit = async (e:any)=>{
  e.preventDefault();
  const tok = await login(u,p)
  localStorage.setItem('token', tok.access_token)
  location.href='/dashboard'
 }
 return (
  <form onSubmit={submit} className="max-w-sm mx-auto mt-20 bg-white p-6 rounded shadow">
   <h1 className="text-xl font-semibold mb-4">Entrar</h1>
   <input value={u} onChange={e=>setU(e.target.value)} className="w-full mb-2 border p-2" placeholder="Usuário" />   
   <input value={p} onChange={e=>setP(e.target.value)} className="w-full mb-4 border p-2" placeholder="Senha" type="password" />
   <button className="bg-blue-600 text-white px-4 py-2 rounded">Entrar</button>
  </form>
 )
}
