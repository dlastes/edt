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

export class Time {
  value: number
  text: string

  constructor (value: number, text: string) {
    this.value = value
    this.text = text
  }
}

export interface WeekDay {
  date: string
  name: string
  num: number
  ref: string
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

export class Course {
  id: number
  week: string
  year: string
  no: number
  type: { department: { name: string }, name: string }
  room_type: { name: string }
  tutor: string
  supp_tutor: string
  groups: Array<{ name: string }>
  module: { abbrev: string }
  modulesupp: { abbrev: string }
  pay_module: { abbrev: string }

  constructor () {
    this.id = 0
    this.week = ''
    this.year = ''
    this.no = 0
    this.type = {department: {name: ''}, name: ''}
    this.room_type = {name: ''}
    this.tutor = ''
    this.supp_tutor = ''
    this.groups = []
    this.module = {abbrev: ''}
    this.modulesupp = {abbrev: ''}
    this.pay_module = {abbrev: ''}
  }
}

export class ScheduledCourse {
  id: number
  room: number
  start_time: number
  day: string
  course: {
    id: number
    type: string
    room_type: string
    week: number
    year: number
    groups: [
      {
        id: number
        train_prog: string
        name: string
        is_structural: boolean
      }
    ]
    supp_tutor: []
    module: {
      name: string
      abbrev: string
      display: {
        color_bg: string
        color_txt: string
      }
    }
    pay_module: object
    is_graded: boolean
  }
  tutor: string
  id_visio: number

  constructor () {
    this.id = 0
    this.room = 0
    this.start_time = 0
    this.day = ''
    this.course = {
      id: 0,
      type: '',
      room_type: '',
      week: 0,
      year: 0,
      groups: [
        {
          id: 0,
          train_prog: '',
          name: '',
          is_structural: false,
        },
      ],
      supp_tutor: [],
      module: {
        name: '',
        abbrev: '',
        display: {
          color_bg: '',
          color_txt: '',
        },
      },
      pay_module: {},
      is_graded: false,
    }
    this.tutor = ''
    this.id_visio = 0
  }
}

export interface CourseType {
  name: string
  duration: number
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

export class CalendarScheduledCourseSlotElement extends CalendarSlotElement {
  course: ScheduledCourse

  constructor () {
    super()
    this.course = new ScheduledCourse()
  }
}

export interface CalendarSlotInterface {
  openContextMenu: () => boolean,
  closeContextMenu: () => boolean,
}
