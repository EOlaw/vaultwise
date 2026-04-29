"use client"

import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

const colors = ["#27866d", "#d65f50", "#b38a2e", "#3478a6", "#7b5ba7", "#587f5e"]

export function CashFlowChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data}>
        <CartesianGrid stroke="#e7ece8" vertical={false} />
        <XAxis dataKey="month" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} width={42} />
        <Tooltip />
        <Area type="monotone" dataKey="income" stroke="#27866d" fill="#dceee8" strokeWidth={2} />
        <Area type="monotone" dataKey="expenses" stroke="#d65f50" fill="#f7ded9" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export function CategoryPie({ data }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="amount" nameKey="category" outerRadius={76} innerRadius={42}>
          {data.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function BudgetBars({ data }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <CartesianGrid stroke="#e7ece8" vertical={false} />
        <XAxis dataKey="category" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} width={34} />
        <Tooltip />
        <Bar dataKey="progress" fill="#3478a6" radius={[5, 5, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
