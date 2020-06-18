//Tooltips
//Vertical Timeline
tippy('.paragraph__timeline:not(.--is-horizontal) .paragraph__timeline__entry.--is-completed', { content: 'Completed', placement: 'top'})
tippy('.paragraph__timeline:not(.--is-horizontal) .paragraph__timeline__entry.--is-inprogress', { content: 'In Progress', placement: 'top'})
tippy('.paragraph__timeline:not(.--is-horizontal) .paragraph__timeline__entry.--is-pending', { content: 'Pending', placement: 'top'})
//Horizontal Timeline
if($(window).width() >= 992) {
  tippy('.paragraph__timeline.--is-horizontal .paragraph__timeline__entry.--is-completed', { content: 'Completed', distance: 3, offset: -20, placement: 'top-end' })
  tippy('.paragraph__timeline.--is-horizontal .paragraph__timeline__entry.--is-inprogress', { content: 'In Progress', distance: 3, offset: -20, placement: 'top-end' })
  tippy('.paragraph__timeline.--is-horizontal .paragraph__timeline__entry.--is-pending', { content: 'Pending', distance: 3, offset: -20, placement: 'top-end' })
};