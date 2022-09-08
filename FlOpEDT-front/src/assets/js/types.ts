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
