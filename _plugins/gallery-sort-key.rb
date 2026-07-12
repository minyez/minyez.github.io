# frozen_string_literal: true

require 'date'

module GallerySortKey
  module_function

  DATE_PATTERN = /(?<!\d)\d{4}(?:-\d{1,2}(?:-\d{1,2})?)?(?!\d)/.freeze

  def sort_key(doc)
    date_value = doc.data['date']
    return normalize_date(date_value) if date_value

    period_value = doc.data['period']
    return normalize_period(period_value) if period_value

    '0000-00-00'
  end

  def normalize_date(value)
    case value
    when Time
      value.strftime('%Y-%m-%d')
    when Date
      value.strftime('%Y-%m-%d')
    else
      normalize_date_string(value.to_s)
    end
  rescue ArgumentError
    '0000-00-00'
  end

  def normalize_period(value)
    token = value.to_s.split.reverse.find { |part| part.match?(/\d/) }
    return '0000-00-00' unless token

    date_text = token.scan(DATE_PATTERN).last
    return '0000-00-00' unless date_text

    normalize_date_string(date_text)
  rescue ArgumentError
    '0000-00-00'
  end

  def normalize_date_string(value)
    case value
    when /\A(\d{4})-(\d{1,2})-(\d{1,2})\z/
      Date.new(Regexp.last_match(1).to_i, Regexp.last_match(2).to_i, Regexp.last_match(3).to_i).strftime('%Y-%m-%d')
    when /\A(\d{4})-(\d{1,2})\z/
      year = Regexp.last_match(1).to_i
      month = Regexp.last_match(2).to_i
      Date.new(year, month, 1).next_month.prev_day.strftime('%Y-%m-%d')
    when /\A(\d{4})\z/
      "#{Regexp.last_match(1)}-12-31"
    else
      Date.parse(value).strftime('%Y-%m-%d')
    end
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  galleries = site.collections['galleries']
  next unless galleries

  galleries.docs.each do |doc|
    doc.data['gallery_sort_date'] = GallerySortKey.sort_key(doc)
  end
end
