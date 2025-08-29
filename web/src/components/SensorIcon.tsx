export default function SensorIcon({icon}:{icon:string}){
 const map:any = {
  thermometer: '🌡️',
  water_drop: '💧',
  humidity: '💦',
  power: '⚡'
 }
 return <span className="text-2xl select-none">{map[icon] || '📟'}</span>
}
