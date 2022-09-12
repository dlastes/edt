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

export class Room {
  departments: Array<number>
  id: number
  name: string
  subroom_of: Array<Room>
  types: Array<number>

  constructor () {
    this.departments = []
    this.id = 0
    this.name = ''
    this.subroom_of = []
    this.types = []
  }
}

export class RoomReservation {
  date: string
  description: string
  email: boolean
  end_time: string
  id: number
  responsible: string
  room: Room
  start_time: string
  title: string
  with_key: boolean

  constructor () {
    this.date = ''
    this.description = ''
    this.email = false
    this.end_time = ''
    this.id = 0
    this.responsible = ''
    this.room = new Room()
    this.start_time = ''
    this.title = ''
    this.with_key = false
  }
}

export class CalendarSlotElement {
  startTime: Time
  endTime: Time
  title: string

  constructor () {
    this.startTime = {value: 0, text: ''}
    this.endTime = {value: 0, text: ''}
    this.title = ''
  }
}

export class CalendarRoomReservationSlotElement extends CalendarSlotElement {
  reservation: RoomReservation

  constructor () {
    super()
    this.reservation = new RoomReservation()
  }
}

export interface CalendarSlotInterface {
  openContextMenu: () => boolean,
  closeContextMenu: () => boolean,
}
