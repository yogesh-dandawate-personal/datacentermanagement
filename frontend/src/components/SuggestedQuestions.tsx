/**
 * Suggested Questions Component
 * Displays suggested questions for the user to click
 */

import { CopilotQuestion } from '../types/copilot'
import { Button } from './ui/Button'
import { Lightbulb } from 'lucide-react'

interface SuggestedQuestionsProps {
  questions: CopilotQuestion[]
  onQuestionClick: (question: string) => void
  isLoading?: boolean
}

export function SuggestedQuestions({
  questions,
  onQuestionClick,
  isLoading = false
}: SuggestedQuestionsProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-slate-400">
        <Lightbulb className="w-4 h-4" />
        <span className="text-sm font-medium">Suggested Questions</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {questions.map(question => (
          <Button
            key={question.id}
            variant="outline"
            onClick={() => onQuestionClick(question.text)}
            disabled={isLoading}
            className="text-left h-auto py-2 px-3 text-xs"
            title={question.text}
            aria-label={`Ask: ${question.text}`}
          >
            <span className="text-slate-300 hover:text-white transition-colors truncate">
              {question.text}
            </span>
          </Button>
        ))}
      </div>
    </div>
  )
}
