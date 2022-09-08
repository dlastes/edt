export interface FlopWeek {
  week: number,
  year: number,
}

export interface TimeSettings {
  'id': number,
  'day_start_time': number,
  'day_finish_time': number,
  'lunch_break_start_time': number,
  'lunch_break_finish_time': number,
  'days': Array<string>,
  'default_preference_duration': number,
  'department': number
}

export interface Time {
  value: number,
  text: string,
}

export interface Department {
  id: number,
  abbrev: string,
}

export interface Room {
  departments: Array<number>,
  id: number,
  name: string,
  subroom_of: Array<Room>,
  types: Array<number>,
}

export interface RoomReservation {
  date: '2022-09-08',
  description: 'bbb',
  email: false,
  end_time: '02:00:00',
  id: 1,
  responsible: 'QBMW',
  room: Room,
  start_time: '01:00:00',
  title: 'aaa',
  with_key: true,
}
