"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { updateAutomationSchedule } from "@/lib/settings/system/api";
import type { Automation } from "@/types/settings/api";
import { Calendar, Clock } from "lucide-react";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface ScheduleModalProps {
  automation: Automation;
  open: boolean;
  onClose: () => void;
}

export function ScheduleModal({
  automation,
  open,
  onClose,
}: ScheduleModalProps) {
  const [scheduleType, setScheduleType] = useState("daily");
  const [time, setTime] = useState("09:00");
  const [weekday, setWeekday] = useState("monday");
  const [dayOfMonth, setDayOfMonth] = useState("1");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { t } = useAppTranslation("settings_system");

  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: updateAutomationSchedule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automations"] });
      onClose();
    },
  });

  const handleSubmit = () => {
    setIsSubmitting(true);

    let schedule = "";

    switch (scheduleType) {
      case "daily":
        schedule = `Daily at ${time}`;
        break;
      case "weekly":
        schedule = `Every ${weekday} at ${time}`;
        break;
      case "monthly":
        schedule = `Monthly on day ${dayOfMonth} at ${time}`;
        break;
      case "custom":
        schedule = "Custom schedule";
        break;
    }

    updateMutation.mutate({
      id: automation.id,
      schedule,
      scheduleType,
      time,
      weekday,
      dayOfMonth,
    });
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("schedule_automation")}</DialogTitle>
          <DialogDescription>
            {t("configure_when")} {automation.name} {t("should_run")}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <RadioGroup
            defaultValue={scheduleType}
            onValueChange={setScheduleType}
            className="grid grid-cols-2 gap-4"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="daily" id="daily" />
              <Label htmlFor="daily">{t("daily")}</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="weekly" id="weekly" />
              <Label htmlFor="weekly">{t("weekly")}</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="monthly" id="monthly" />
              <Label htmlFor="monthly">{t("monthly")}</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="custom" id="custom" />
              <Label htmlFor="custom">{t("custom")}</Label>
            </div>
          </RadioGroup>

          <div className="grid gap-2">
            <Label htmlFor="time">{t("time")}</Label>
            <div className="flex items-center">
              <Clock className="mr-2 h-4 w-4 text-muted-foreground" />
              <Input
                id="time"
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
              />
            </div>
          </div>

          {scheduleType === "weekly" && (
            <div className="grid gap-2">
              <Label htmlFor="weekday">{t("day_of_week")}</Label>
              <Select value={weekday} onValueChange={setWeekday}>
                <SelectTrigger id="weekday">
                  <SelectValue placeholder="Select day" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="monday">{t("monday")}</SelectItem>
                  <SelectItem value="tuesday">{t("tuesday")}</SelectItem>
                  <SelectItem value="wednesday">{t("Mittwoch")}</SelectItem>
                  <SelectItem value="thursday">{t("thursday")}</SelectItem>
                  <SelectItem value="friday">{t("friday")}</SelectItem>
                  <SelectItem value="saturday">{t("saturday")}</SelectItem>
                  <SelectItem value="sunday">{t("sunday")}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {scheduleType === "monthly" && (
            <div className="grid gap-2">
              <Label htmlFor="dayOfMonth">{t("day_of_month")}</Label>
              <div className="flex items-center">
                <Calendar className="mr-2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="dayOfMonth"
                  type="number"
                  min="1"
                  max="31"
                  value={dayOfMonth}
                  onChange={(e) => setDayOfMonth(e.target.value)}
                />
              </div>
            </div>
          )}

          {scheduleType === "custom" && (
            <div className="grid gap-2">
              <Label htmlFor="cronExpression">{t("cron_expression")}</Label>
              <Input id="cronExpression" placeholder="*/15 * * * *" />
              <p className="text-xs text-muted-foreground mt-1">
                {t("use_cron_syntax")}
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            {t("cancel")}
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? t("saving") : t("save_schedule")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
