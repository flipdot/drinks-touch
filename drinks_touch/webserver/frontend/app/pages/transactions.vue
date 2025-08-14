<template>
  <svg ref="svg"></svg>
</template>

<script setup lang="ts">
import * as d3 from 'd3'

const { data } = await useFetch<
  Array<{
    name: string
    timestamp: string
  }>
>('/transactions', {
  baseURL: 'http://localhost:5002',
})

console.log(data.value)

onMounted(async () => {
  const width = 400,
    height = 300,
    marginTop = 20,
    marginRight = 20,
    marginBottom = 30,
    marginLeft = 20

  // const color = d3.scaleOrdinal(d3.schemeCategory10);
  debugger
  const svg = d3
    .select('svg')
    .attr('width', width + marginRight + marginLeft)
    .attr('height', height + marginTop + marginBottom)
    .append('g')
    .attr('transform', `translate(${marginBottom},${marginTop})`)

  const line = d3
    .line()
    .curve(d3.curveBasis)
    .x((d) => x(d.timestamp))
    .y((d) => y(d.id))

  const axis = d3
    .line()
    .curve(d3.curveBasis)
    .x((d) => x(d.timestamp))
    .y(() => height)

  const area = d3
    .area()
    .curve(d3.curveBasis)
    .x((d) => x(d.date))
    .y1((d) => y(d.price))

  const weekdays = [
    'Sonntag',
    'Montag',
    'Dienstag',
    'Mittwoch',
    'Donnerstag',
    'Freitag',
    'Samstag',
  ]

  if (!data.value) throw createError({ statusCode: 404 })

  const scans = []

  for (const element of data.value) {
    const timestampParsed = d3.isoParse(element.timestamp)

    if (!timestampParsed) continue

    scans.push({ ...element, timestamp: timestampParsed })
  }

  const drinks = d3
    .groups(scans, (d) => d.name)
    .map(([name, group]) => ({
      name: name,
      values: d3
        .groups(group, (d) => weekdays[d.timestamp.getDay()])
        .map(([day, items]) => ({ day, count: items.length })),
      count: group.length,
    }))
  drinks.forEach((d) => {
    d.count = d.values.length
  })
  drinks.sort((a, b) => a.count - b.count)

  svg
    .selectAll('g.drink')
    .data(drinks)
    .enter()
    .append('g')
    .attr('class', 'drink')
    .style('width', (d) => d.count)

  const areas = () =>
    svg
      .selectAll('.drink')
      .attr('transform', (d, i) => `translate(0,${(i * height) / 4 + 10})`)

  setTimeout(areas, 1000)
})
</script>

<style scoped>
svg {
  font-family: 'Helvetica Neue', Helvetica;
}

.line {
  fill: none;
  stroke: #000;
  stroke-width: 2px;
}
</style>
